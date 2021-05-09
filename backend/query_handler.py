import json
import os
import re
from html import unescape
from math import ceil
from typing import List

import mariadb
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.preprocessing import StandardScaler
from xpysom import XPySom

from data_classes import FilterCriteria, Keyframe

HTML_TAG_RE = re.compile(r'<[^>]+>')

prediction_root = os.getenv(key="PREDICTIONS_ROOT",
                            default='C:/Users/41789/Documents/uni/fs21/video_retrieval/')
keyframe_root = os.getenv(key="KEYFRAME_ROOT",
                          default='D:/keyframes/')


def find_index_from_image(img, image_data):  # this function finds the index of the image within the image_data
    for index in range(len(image_data)):
        if (np.array_equal(image_data[index], img)):
            return index


# SELECT distinct video_fk, frame FROM ivr.nasnet_classification where class in ('suit', 'lab_coat') and confidence > 0.25 order by rand() limit 250;
# SELECT video_fk, frame FROM ivr.yolo_detection ivr1 where ivr1.class = 'sink' and ivr1.confidence > 0.5 and
# exists(select video_fk, frame from ivr.yolo_detection ivr2 where ivr2.class = 'person' and ivr2.confidence > 0.5 and ivr2.video_fk = ivr1.video_fk and ivr2.frame = ivr1.frame);

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
        self.cursor = self.db_connection.cursor()

        self.cursor.execute(
            "SELECT id,title FROM videos WHERE id=?",
            ('00032',))

        if self.cursor.fetchone() is None:
            jsons = []
            for filename in os.listdir("C:/Users/41789/Documents/uni/fs21/video_retrieval/info"):
                with open(os.path.join("C:/Users/41789/Documents/uni/fs21/video_retrieval/info", filename), 'r',
                          encoding="latin-1") as f:  # open in readonly mode
                    json_obj = json.loads(f.read().encode("utf8"))
                    jsons.append((json_obj['v3cId'], json_obj['title'], json.dumps(json_obj['tags']),
                                  unescape(' '.join(HTML_TAG_RE.sub('', json_obj['description']).split()))))
            sql = "INSERT INTO videos(id, title, tags, description) VALUES (?, ?, ?, ?)"
            self.cursor.executemany(sql, jsons)
            self.db_connection.commit()
        else:
            print("Video table is ready!")

        self.cursor.execute(
            "SELECT video_fk,frame FROM keyframes WHERE video_fk=?",
            ('00032',))

        if self.cursor.fetchone() is None:
            data = []
            for index, row in self.keyframe_data.iterrows():
                data.append((row['keyframe'].split("_")[0], int(row['keyframe'].split("_")[1]),
                             row['starttime'], row['endtime']
                             ))
            sql = "INSERT INTO keyframes(video_fk, frame, start_time, end_time) " \
                  "VALUES (?, ?, ?, ?)"
            self.cursor.executemany(sql, data)
            self.db_connection.commit()
        else:
            print("Keyframe table is ready!")

        self.cursor.execute(
            "SELECT video_fk FROM yolo_detection WHERE video_fk=?",
            ('00032',))

        if self.cursor.fetchone() is None:
            data = []
            for index, row in self.yolo.iterrows():
                data.append((row['video'], int(row['frame']),
                             row['class'], float(row['centerX']), float(row['centerY']), float(row['width']),
                             float(row['height']), float(row['confidence'])
                             ))
            sql = "INSERT INTO yolo_detection(video_fk, frame, class, center_x, center_y, width, height, confidence) " \
                  "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            self.cursor.executemany(sql, data)
            self.db_connection.commit()
        else:
            print("Yolo table is ready!")

        self.cursor.execute(
            "SELECT video_fk FROM nasnet_classification WHERE video_fk=?",
            ('00032',))

        if self.cursor.fetchone() is None:
            data = []
            for index, row in self.nasnet.iterrows():
                filename_parts = row['filename'].replace("shot", "").replace("_RKF.png", "").split("_")
                data.append((filename_parts[0], int(filename_parts[1]), row['class'], row['confidence']))
            sql = "INSERT INTO nasnet_classification(video_fk, frame, class, confidence) " \
                  "VALUES (?, ?, ?, ?)"
            self.cursor.executemany(sql, data)
            self.db_connection.commit()
        else:
            print(len(self.nasnet))
            print("Nasnet table is ready!")

        self.cursor.execute(
            "SELECT video_fk FROM tesseract_text WHERE video_fk=?",
            ('00032',))

        if self.cursor.fetchone() is None:
            data = []
            for index, row in self.ocr_data.iterrows():
                filename_parts = row['filename'].replace("shot", "").replace("_RKF.png", "").split("_")
                data.append((filename_parts[0], int(filename_parts[1]), row['output']))
            sql = "INSERT INTO tesseract_text(video_fk, frame, text) " \
                  "VALUES (?, ?, ?)"
            self.cursor.executemany(sql, data)
            self.db_connection.commit()
        else:
            print("Tesseract table is ready!")

        self.cursor.execute('SELECT id, description, tags, title FROM videos')
        self.video_map = {}
        for vid_id, description, tags, title in self.cursor.fetchall():
            self.video_map[vid_id] = (description, tags, title)

        print("Initialized query handler")

    def get_shots_based_on_yolo_position_and_class(self, yolo, query_position, class_query):
        query_filter = yolo[yolo["class"] == class_query]
        b = query_position
        confidence_filter = query_filter[query_filter["confidence"] >= 0.5]
        confidence_filter["distance_to_query"] = confidence_filter.apply(lambda row: np.linalg.norm((row['centerX'],
                                                                                                     row[
                                                                                                         'centerY']) - b),
                                                                         axis=1)
        position_filter = confidence_filter[confidence_filter["distance_to_query"] < 0.1]["filename"]
        query_result_shotframes = list(
            set(map(lambda x: x[:-8], position_filter)))  # unique frames that contain the class query
        positions = confidence_filter[confidence_filter["distance_to_query"] < 0.1][['filename', 'centerX', 'centerY']]
        positions = positions.sort_values(by='filename')
        sorted_shotframes = positions['filename']
        X = positions['centerX'].to_numpy()
        Y = positions['centerY'].to_numpy()
        numberofshots_in_query = len(X)
        print(numberofshots_in_query)
        sorted_shotframes = list(map(lambda x: x[:-8], sorted_shotframes))  # unique frames that contain the class query
        return sorted_shotframes, numberofshots_in_query

    def get_shots_based_nasnet_class(self, nasnet, class_query):
        query_filter = nasnet[nasnet["class"] == class_query]
        confidence_filter = query_filter[query_filter["confidence"] >= 0.5]["filename"]
        query_result_shotframes = list(
            set(map(lambda x: x[:-8], confidence_filter)))  # unique frames that contain the class query
        sorted_shotframes = sorted(query_result_shotframes)
        numberofshots_in_query = len(sorted_shotframes)
        return sorted_shotframes, numberofshots_in_query

    def get_shots_based_ocr_text(self, ocr_data, text_query):
        sorted_shotframes = sorted(ocr_data[ocr_data['output'].str.contains(text_query)]["filename"])
        query_result_shotframes = list(map(lambda x: x[:-8], sorted_shotframes))
        numberofshots_in_query = len(query_result_shotframes)
        return query_result_shotframes, numberofshots_in_query

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
        number_of_yolo_queries = len(filter_criteria.locatedObjects)
        number_of_nasnet_queries = len(filter_criteria.classNames)
        sorted_shotframes = list()

        if number_of_yolo_queries > 0:
            # get filtercriterias from canvas
            yolo_class_query = filter_criteria.locatedObjects[0].className
            x_offset = filter_criteria.locatedObjects[0].xOffset
            y_offset = filter_criteria.locatedObjects[0].yOffset
            width = filter_criteria.locatedObjects[0].width
            height = filter_criteria.locatedObjects[0].height

            # parse position to float between 0 and 1.
            # to do: access information in isLargeScreen, if no, 640 -> 344px, and 360 -> 171
            x_position = (x_offset + (width / 2)) / 640
            y_position = (y_offset + (height / 2)) / 360
            queryPosition = np.array((x_position, y_position))
            sorted_shotframes, numberofshots_in_query = self.get_shots_based_on_yolo_position_and_class(self.yolo,
                                                                                                        queryPosition,
                                                                                                        yolo_class_query)
            print("Yolo length", numberofshots_in_query)

        if number_of_nasnet_queries > 0:
            # get filter criterias Nasnet
            nasnet_class_query = filter_criteria.classNames[0]
            print("Nasnet query:", nasnet_class_query)
            sorted_shotframes_nasnet, numberofshots_in_query = self.get_shots_based_nasnet_class(self.nasnet,
                                                                                                 nasnet_class_query)
            print("Nasnet length", numberofshots_in_query)
            if len(sorted_shotframes) > 0:
                sorted_shotframes = np.intersect1d(sorted_shotframes, sorted_shotframes_nasnet)
            else:
                sorted_shotframes = sorted_shotframes_nasnet

        if filter_criteria.text is not None:
            # get filter criterias text (OCR)
            text_query = filter_criteria.text
            print("text query:", text_query)
            sorted_shotframes_text, numberofshots_in_query = self.get_shots_based_ocr_text(self.ocr_data, text_query)
            if len(sorted_shotframes) > 0:
                sorted_shotframes = np.intersect1d(sorted_shotframes, sorted_shotframes_text)
            else:
                sorted_shotframes = sorted_shotframes_text

        print("Final length", len(sorted_shotframes))

        all_kf_test = list(
            map(lambda x: keyframe_root + x[4:9] + "/" + x + "_RKF.png", sorted_shotframes))

        # 1: Laura filters the keyframes
        print("Filtered all keyframes")
        # 2: Baris does the SOM on the keyframes
        if len(all_kf_test) > 0:
            som_map = self.produce_SOM_grid(all_kf_test,
                                            filter_criteria.gridWidth,
                                            ceil(float(len(all_kf_test)) / filter_criteria.gridWidth),
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
                                 description=description, tags=json.loads(tags.replace("'", '"'))).to_dict())
                else:
                    som_correct_paths.append(None)
            som_correct_paths_complete.append(som_correct_paths)
        print("corrected som:", som_correct_paths_complete)

        return som_correct_paths_complete
