import json
import os
import random
from math import ceil
from typing import List

import mariadb
import numpy as np
from PIL import Image
from sklearn.preprocessing import StandardScaler
from xpysom import XPySom

from data_classes import FilterCriteria, Keyframe, RandomVideo, KeyframeFilterCriteria

prediction_root = os.getenv(key="PREDICTIONS_ROOT",
                            default='C:/Users/41789/Documents/uni/fs21/video_retrieval/')
keyframe_root = os.getenv(key="KEYFRAME_ROOT",
                          default='D:/keyframes/')


def find_index_from_image(img, image_data):  # this function finds the index of the image within the image_data
    for index in range(len(image_data)):
        if (np.array_equal(image_data[index], img)):
            return index


class QueryHandler:
    def __init__(self):
        self.db_connection = mariadb.connect(user=os.getenv("db_user"), password=os.getenv("db_pw"),
                                             database=os.getenv("db_name"), host=os.getenv("db_host"), port=3306)
        self.db_connection.auto_reconnect = True
        print("Initialized query handler")

    def random_visual_known_item(self) -> RandomVideo:
        cursor = self.db_connection.cursor()
        cursor.execute(
            "SELECT id, vimeo_id, floor(max(keyframes.end_time)) - 20 from videos "
            "join keyframes on videos.id = keyframes.video_fk "
            "group by keyframes.video_fk "
            "order by rand() limit 1")
        sql_result = cursor.fetchone()
        cursor.close()
        print("Random video result:", sql_result)
        return RandomVideo(id=sql_result[0], vimeoId=sql_result[1], atTime=random.randint(0, int(sql_result[2])))

    def produce_SOM_grid(self, shot_locations, grid_w, grid_h, it=10):
        image_data = []
        width = 200
        height = 113
        dim = (width, height)

        for loc in shot_locations:
            # Load the image and convert to 24-bit RGB because some of our images are 32-bit RGBA
            img = Image.open(loc).convert('RGB')

            resized = img.resize(dim)

            image_data.append(np.reshape(resized, (np.prod(np.shape(resized)))))

        scaler = StandardScaler()
        image_data = scaler.fit_transform(image_data)

        som_gpu = XPySom(grid_h, grid_w, len(image_data[0]), random_seed=7)

        som_gpu.train(image_data, it, verbose=False)
        win_map = som_gpu.win_map(
            image_data)  # this win_map is actually the positions of the winning neurons for each image_data, could be empty

        position_grid = np.zeros((grid_h, grid_w), dtype=int)

        to_fill = []
        collided = []

        for i in range(grid_w * grid_h):
            position = np.unravel_index(i, (grid_h, grid_w))
            if position in win_map:
                img = win_map[position][0]
                collided += win_map[position][
                            1:]  # collided is actually the places within the grid where the win_map produced more than one image so we just take one and add the others into collided array
                position_grid[position] = find_index_from_image(img,
                                                                image_data)  # we simply put to the grid the one that we encounter first for the position
            else:
                to_fill.append(
                    i)  # in the win_map, some positions are not filled, so the win_map did not put any image to a position so we put the index of those positions in the to_fill(not the positions but their index i for the grid[i] (handled by the grid structure)
        collided = collided[::-1]
        for i in to_fill:
            position = np.unravel_index(i, (grid_h, grid_w))
            if len(collided) > 0:
                img = collided.pop()
                index = find_index_from_image(img, image_data)
                position_grid[
                    position] = index  # for the places that are not filled by the win_map, we put the collided images in order
            else:
                position_grid[position] = -1
        location_grid = np.empty_like(position_grid, dtype=object)
        for row_index, row in enumerate(position_grid):
            for column_index, shot_index in enumerate(row):
                if shot_index != -1:
                    location_grid[row_index][column_index] = shot_locations[shot_index]
                else:
                    location_grid[row_index][column_index] = None
        return location_grid

    def get_first_item_sql(self, kf_filter: KeyframeFilterCriteria):
        number_of_localization_queries = len(kf_filter.locatedObjects)
        number_of_class_queries = len(kf_filter.classNames)
        number_of_count_queries = len(kf_filter.quantities)

        # 1: We filter the keyframes
        sql_statement = "SELECT kf.video_fk, kf.frame, kf.start_time, vid.vimeo_id, vid.description, vid.tags, " \
                        "vid.title, (SELECT max(kf2.frame) from ivr.keyframes kf2 where kf2.video_fk = kf.video_fk) as max_vid " \
                        "FROM ivr.keyframes kf join ivr.videos vid on vid.id = kf.video_fk where 1"
        sql_data = []

        # by keyframe class (nasnet)
        if number_of_class_queries > 0:
            sql_statement += " and exists(select 1 from ivr.nasnet_classification cls2 where " \
                             "cls2.video_fk = kf.video_fk and cls2.frame = kf.frame and cls2.class in " \
                             "(" + ",".join(["?"] * number_of_class_queries) + ") and cls2.confidence >= 0.5)"
            sql_data = sql_data + kf_filter.classNames

        # by text in keyframe (tesseract)
        if kf_filter.text is not None and kf_filter.text != "":
            sql_statement += " and exists(select 1 from ivr.tesseract_text ivrt where " \
                             "ivrt.video_fk = kf.video_fk and ivrt.frame = kf.frame and ivrt.text like ?)"
            sql_data = sql_data + ["%" + kf_filter.text + "%"]

        for i in range(0, number_of_localization_queries):
            localization_filter = kf_filter.locatedObjects[i]
            yolo_table_name = "yolo" + str(i)
            center_x = localization_filter.xOffset + localization_filter.width / 2
            center_y = localization_filter.yOffset + localization_filter.height / 2
            sql_statement += f' and exists(select 1=1 from ivr.yolo_detection {yolo_table_name} where ' \
                             f'{yolo_table_name}.video_fk = kf.video_fk and {yolo_table_name}.frame = kf.frame and ' \
                             f'{yolo_table_name}.class = ? and ' \
                             f'{yolo_table_name}.center_x between ? and ? and {yolo_table_name}.center_y between ? and ? and ' \
                             f'{yolo_table_name}.width between ? and ? and {yolo_table_name}.height between ? and ? and ' \
                             f'{yolo_table_name}.confidence >= 0.5)'
            sql_data = sql_data + [localization_filter.className, center_x - 0.15, center_x + 0.15, center_y - 0.15,
                                   center_y + 0.15, localization_filter.width - 0.15, localization_filter.width + 0.15,
                                   localization_filter.height - 0.15, localization_filter.height + 0.15]

        for i in range(0, number_of_count_queries):
            min_count_table_name = "mc" + str(i)
            obj = kf_filter.quantities[i]

            if obj.minQuantity == 0 and obj.maxQuantity == 0:
                sql_statement += f' and (kf.video_fk, kf.frame) not in (select {min_count_table_name}.video_fk, {min_count_table_name}.frame from ivr.yolo_detection {min_count_table_name} where ' \
                                 f'{min_count_table_name}.class = ? and {min_count_table_name}.confidence >= 0.5 group by {min_count_table_name}.video_fk, {min_count_table_name}.frame having count(*) >= 1)'
                sql_data = sql_data + [obj.className, obj.minQuantity]
            else:
                sql_statement += f' and (kf.video_fk, kf.frame) in (select {min_count_table_name}.video_fk, {min_count_table_name}.frame from ivr.yolo_detection {min_count_table_name} where ' \
                                 f'{min_count_table_name}.class = ? and {min_count_table_name}.confidence >= 0.5 group by {min_count_table_name}.video_fk, {min_count_table_name}.frame having count(*) '
                # case distiction: 15 means 15+, else is range
                if obj.maxQuantity == 15:
                    sql_statement += ">= ?)"
                    sql_data = sql_data + [obj.className, obj.minQuantity]
                else:
                    sql_statement += "between ? and ?)"
                    sql_data = sql_data + [obj.className, obj.minQuantity, obj.maxQuantity]
        return sql_statement, sql_data

    def get_nth_elem_sql(self, kf_filter: KeyframeFilterCriteria, n: int = 1):
        number_of_localization_queries = len(kf_filter.locatedObjects)
        number_of_class_queries = len(kf_filter.classNames)
        number_of_count_queries = len(kf_filter.quantities)

        previous_kf = "kf"
        if n > 1:
            previous_kf = "kf2" + str(n - 1)
        kf_table_name = "kf2" + str(n)
        # 1: We filter the keyframes
        sql_statement = f' and exists(select 1 from ivr.keyframes {kf_table_name} where ' \
                        f'{kf_table_name}.video_fk = {previous_kf}.video_fk and ' \
                        f'{kf_table_name}.frame > {previous_kf}.frame'
        sql_data = []

        # by keyframe class (nasnet)
        if number_of_class_queries > 0:
            nas_class = "nas_cls" + str(n)
            sql_statement += f' and exists(select 1 from ivr.nasnet_classification {nas_class} where ' \
                             f'{nas_class}.video_fk = {kf_table_name}.video_fk and ' \
                             f'{nas_class}.frame = {kf_table_name}.frame ' \
                             f'and {nas_class}.class in ({",".join(["?"] * number_of_class_queries)}) ' \
                             f'and {nas_class}.confidence >= 0.5)'
            sql_data = sql_data + kf_filter.classNames

        # by text in keyframe (tesseract)
        if kf_filter.text is not None and kf_filter.text != "":
            tess_txt = "tess_txt" + str(n)
            sql_statement += f' and exists(select 1 from ivr.tesseract_text {tess_txt} where ' \
                             f'{tess_txt}.video_fk = {kf_table_name}.video_fk and ' \
                             f'{tess_txt}.frame = {kf_table_name}.frame and {tess_txt}.text like ?)'
            sql_data = sql_data + ["%" + kf_filter.text + "%"]

        for i in range(0, number_of_localization_queries):
            localization_filter = kf_filter.locatedObjects[i]
            yolo_table_name = "yolo" + str(n) + "q" + str(i)
            center_x = localization_filter.xOffset + localization_filter.width / 2
            center_y = localization_filter.yOffset + localization_filter.height / 2
            sql_statement += f' and exists(select 1=1 from ivr.yolo_detection {yolo_table_name} where ' \
                             f'{yolo_table_name}.video_fk = {kf_table_name}.video_fk and ' \
                             f'{yolo_table_name}.frame = {kf_table_name}.frame and ' \
                             f'{yolo_table_name}.class = ? and ' \
                             f'{yolo_table_name}.center_x between ? and ? and {yolo_table_name}.center_y between ? and ? and ' \
                             f'{yolo_table_name}.width between ? and ? and {yolo_table_name}.height between ? and ? and ' \
                             f'{yolo_table_name}.confidence >= 0.5)'
            sql_data = sql_data + [localization_filter.className, center_x - 0.15, center_x + 0.15, center_y - 0.15,
                                   center_y + 0.15, localization_filter.width - 0.15, localization_filter.width + 0.15,
                                   localization_filter.height - 0.15, localization_filter.height + 0.15]

        for i in range(0, number_of_count_queries):
            min_count_table_name = "mc" + str(n) + "q" + str(i)
            obj = kf_filter.quantities[i]

            if obj.minQuantity == 0 and obj.maxQuantity == 0:
                sql_statement += f' and ({kf_table_name}.video_fk, {kf_table_name}.frame) not in ' \
                                 f'(select {min_count_table_name}.video_fk, {min_count_table_name}.frame from ivr.yolo_detection {min_count_table_name} where ' \
                                 f'{min_count_table_name}.class = ? and {min_count_table_name}.confidence >= 0.5 group by {min_count_table_name}.video_fk, {min_count_table_name}.frame having count(*) >= 1)'
                sql_data = sql_data + [obj.className, obj.minQuantity]
            else:
                sql_statement += f' and ({kf_table_name}.video_fk, {kf_table_name}.frame) in (select {min_count_table_name}.video_fk, {min_count_table_name}.frame from ivr.yolo_detection {min_count_table_name} where ' \
                                 f'{min_count_table_name}.class = ? and {min_count_table_name}.confidence >= 0.5 group by {min_count_table_name}.video_fk, {min_count_table_name}.frame having count(*) '
                # case distiction: 15 means 15+, else is range
                if obj.maxQuantity == 15:
                    sql_statement += ">= ?)"
                    sql_data = sql_data + [obj.className, obj.minQuantity]
                else:
                    sql_statement += "between ? and ?)"
                    sql_data = sql_data + [obj.className, obj.minQuantity, obj.maxQuantity]

        return sql_statement, sql_data

    def handle_query(self, filter_criteria: FilterCriteria) -> List[List[Keyframe]]:
        print("Filtering according to criteria", filter_criteria)

        if len(filter_criteria.frames) == 0:
            print("No filters defined!")
            return [[]]

        sql_statement, sql_data = self.get_first_item_sql(filter_criteria.frames[0])

        for i in range(1, len(filter_criteria.frames)):
            sql_statement_it, sql_data_it = self.get_nth_elem_sql(filter_criteria.frames[i], i)
            sql_statement += sql_statement_it
            sql_data = sql_data + sql_data_it

        sql_statement += ("".join([")"] * (len(filter_criteria.frames) - 1)))

        limit = min(12 * 12, filter_criteria.gridWidth * 12)
        sql_statement += " order by rand() limit " + str(limit)
        print("SQL statement:", sql_statement)
        print("SQL data:", sql_data)
        cursor = self.db_connection.cursor()
        cursor.execute(sql_statement, tuple(sql_data))
        sql_result = cursor.fetchall()
        cursor.close()
        print("SQL result:", sql_result)

        all_results = {keyframe_root + video + "/shot" + video + "_" + str(frame) + "_RKF.png":
                           Keyframe(title=title, video=video, idx=frame, totalKfsVid=max_frame,
                                    atTime=str(ceil(start_time)) + "s",
                                    description=description, vimeoId=vimeo_id,
                                    tags=json.loads(tags)).to_dict() for
                       video, frame, start_time, vimeo_id, description, tags, title, max_frame in
                       sql_result}
        all_kf = list(all_results.keys())
        print("Filtered keyframes, result length:", len(all_kf))

        # 2: We do the SOM on the keyframes
        if len(all_kf) > 0:
            som_map = self.produce_SOM_grid(all_kf,
                                            filter_criteria.gridWidth,
                                            ceil(float(len(all_kf)) / filter_criteria.gridWidth),
                                            10)
        else:
            som_map = np.array([[]])
        list_som = som_map.tolist()

        som_correct_paths_complete = []

        for x in list_som:
            som_correct_paths = []
            for element in x:
                if element is not None:
                    som_correct_paths.append(all_results[element])
                else:
                    som_correct_paths.append(None)
            som_correct_paths_complete.append(som_correct_paths)
        print("Returning som:", som_correct_paths_complete)

        return som_correct_paths_complete
