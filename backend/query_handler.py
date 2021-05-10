import json
import os
from math import ceil
from typing import List

import mariadb
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.preprocessing import StandardScaler
from xpysom import XPySom

from data_classes import FilterCriteria, Keyframe

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
        self.nasnet = pd.read_csv(prediction_root + 'nasnet_formated.csv')
        self.yolo = pd.read_csv(prediction_root + 'yolo.csv',
                                index_col="idx", dtype=str)
        self.ocr_data = pd.read_csv(prediction_root + 'combinedOCR.csv').dropna(
            subset=['output'])
        self.keyframe_data = pd.read_csv(prediction_root + 'timeframes.csv')
        self.db_connection = mariadb.connect(user=os.getenv("db_user"), password=os.getenv("db_pw"),
                                             database=os.getenv("db_name"), host=os.getenv("db_host"), port=3307)
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT id, description, tags, title FROM videos')
        self.video_map = {}
        for vid_id, description, tags, title in cursor.fetchall():
            self.video_map[vid_id] = (description, tags, title)

        cursor.close()
        print("Initialized query handler")

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

    def handle_query(self, filter_criteria: FilterCriteria) -> List[List[Keyframe]]:
        print("Filtering according to criteria", filter_criteria)
        number_of_localization_queries = len(filter_criteria.locatedObjects)
        number_of_class_queries = len(filter_criteria.classNames)
        number_of_count_queries = len(filter_criteria.minQuantities)

        # 1: We filter the keyframes
        sql_statement = "SELECT kf.video_fk, kf.frame FROM ivr.keyframes kf where 1=1"
        sql_data = []

        # by keyframe class (nasnet)
        if number_of_class_queries > 0:
            sql_statement += " and exists(select 1 from ivr.nasnet_classification cls2 where " \
                             "cls2.video_fk = kf.video_fk and cls2.frame = kf.frame and cls2.class in " \
                             "(" + ",".join(["?"] * number_of_class_queries) + ") and cls2.confidence >= 0.5)"
            sql_data = sql_data + filter_criteria.classNames

        # by text in keyframe (tesseract)
        if filter_criteria.text is not None and filter_criteria.text != "":
            sql_statement += " and exists(select 1 from ivr.tesseract_text ivrt where " \
                             "ivrt.video_fk = kf.video_fk and ivrt.frame = kf.frame and ivrt.text like ?)"
            sql_data = sql_data + ["%" + filter_criteria.text + "%"]

        for i in range(0, number_of_localization_queries):
            localization_filter = filter_criteria.locatedObjects[i]
            yolo_table_name = "yolo" + str(i)
            center_x = localization_filter.xOffset + localization_filter.width / 2
            center_y = localization_filter.yOffset + localization_filter.height / 2
            sql_statement += f' and exists(select 1=1 from ivr.yolo_detection {yolo_table_name} where ' \
                             f'{yolo_table_name}.video_fk = kf.video_fk and {yolo_table_name}.frame = kf.frame and ' \
                             f'{yolo_table_name}.class = ? and ' \
                             f'{yolo_table_name}.center_x between ? and ? and {yolo_table_name}.center_y between ? and ? and ' \
                             f'{yolo_table_name}.width between ? and ? and {yolo_table_name}.height between ? and ? and ' \
                             f'{yolo_table_name}.confidence >= 0.5)'
            sql_data = sql_data + [localization_filter.className, center_x - 0.1, center_x + 0.1, center_y - 0.1,
                                   center_y + 0.1, localization_filter.width - 0.1, localization_filter.width + 0.1,
                                   localization_filter.height - 0.1, localization_filter.height + 0.1]

        for i in range(0, number_of_count_queries):
            min_count_table_name = "mc" + str(i)
            obj = filter_criteria.minQuantities[i]
            sql_statement += f' and (kf.video_fk, kf.frame) in (select {min_count_table_name}.video_fk, {min_count_table_name}.frame from ivr.yolo_detection {min_count_table_name} where ' \
                             f'{min_count_table_name}.class = ? group by {min_count_table_name}.video_fk, {min_count_table_name}.frame having count(*) >= ?)'
            sql_data = sql_data + [obj.className, obj.minQuantity]

        limit = min(200, filter_criteria.gridWidth * 25)
        sql_statement += " order by rand() limit " + str(limit)
        print("SQL statement:", sql_statement)
        print("SQL data:", sql_data)
        cursor = self.db_connection.cursor()
        cursor.execute(sql_statement, tuple(sql_data))
        sql_result = cursor.fetchall()
        cursor.close()
        print("SQL result:", sql_result)

        all_kf = [(keyframe_root + video + "/shot" + video + "_" + str(frame) + "_RKF.png") for video, frame in
                  sql_result]
        print("Final length", len(sql_result))
        print("Filtered all keyframes")

        # 2: We do the SOM on the keyframes
        if len(all_kf) > 0:
            som_map = self.produce_SOM_grid(all_kf,
                                            filter_criteria.gridWidth,
                                            ceil(float(len(all_kf)) / filter_criteria.gridWidth),
                                            10)
        else:
            som_map = np.array([[]])
        list_som = som_map.tolist()

        print("Done som:", list_som)

        som_correct_paths_complete = []

        for x in list_som:
            som_correct_paths = []
            for element in x:
                if element is not None:
                    video, kf_idx = element.replace(keyframe_root, "").split("/")[1].replace("shot", "").replace(
                        "_RKF.png", "").split("_")
                    description, tags, title = self.video_map[video]
                    som_correct_paths.append(
                        Keyframe(title=title, video=video, idx=int(kf_idx), totalKfsVid=int(kf_idx), atTime="00:01:10",
                                 description=description, tags=json.loads(tags)).to_dict())
                else:
                    som_correct_paths.append(None)
            som_correct_paths_complete.append(som_correct_paths)
        print("corrected som:", som_correct_paths_complete)

        return som_correct_paths_complete
