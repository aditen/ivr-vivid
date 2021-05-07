import os
from math import ceil
from typing import List

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
                                index_col="idx")
        self.ocr_data = pd.read_csv(prediction_root + 'combinedOCR.csv').dropna(
            subset=['output'])

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
            print(queryPosition)
            sorted_shotframes, numberofshots_in_query = self.get_shots_based_on_yolo_position_and_class(self.yolo,
                                                                                                        queryPosition,
                                                                                                        yolo_class_query)
            print("Yolo lenght", numberofshots_in_query)

        if number_of_nasnet_queries > 0:
            # get filter criterias Nasnet
            nasnet_class_query = filter_criteria.classNames[0]
            print("Nasnet query:", nasnet_class_query)
            sorted_shotframes_nasnet, numberofshots_in_query = self.get_shots_based_nasnet_class(self.nasnet,
                                                                                                 nasnet_class_query)
            print("Nasnet lenght", numberofshots_in_query)
            if len(sorted_shotframes) > 0:
                sorted_shotframes = np.intersect1d(sorted_shotframes, sorted_shotframes_nasnet)
            else:
                sorted_shotframes = sorted_shotframes_nasnet

        if filter_criteria.text is not None:
            # get filter criterias text (OCR)
            text_query = filter_criteria.text
            print("text query:", text_query)
            sorted_shotframes_text, numberofshots_in_query = self.get_shots_based_ocr_text(self.ocr_data, text_query)
            print("Final lenght", numberofshots_in_query)
            if len(sorted_shotframes) > 0:
                sorted_shotframes = np.intersect1d(sorted_shotframes, sorted_shotframes_text)
            else:
                sorted_shotframes = sorted_shotframes_text

        print("Final length", len(sorted_shotframes))

        all_kf_test = list(
            map(lambda x: keyframe_root + x[4:9] + "/" + x + "_RKF.png", sorted_shotframes))

        # print("real results", all_kf_test)
        # 1: Laura filters the keyframes
        print("Filtered all keyframes")
        print(filter_criteria.gridWidth)
        print(ceil(len(all_kf_test) / filter_criteria.gridWidth))
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
                    parts = element.replace(keyframe_root, "").split("/")[1].replace("shot", "").replace("_RKF.png", "").split("_")
                    som_correct_paths.append(
                        Keyframe(title=parts[0], video=parts[0], idx=int(parts[1]), totalKfsVid=int(parts[1]), atTime="00:01:10",
                                 description="Hello hello from the description", tags=['test1', 'test2']).to_dict())
                else:
                    som_correct_paths.append(
                        Keyframe(title="n/A", video="00032", idx=32, totalKfsVid=32,
                                 atTime="00:01:10", description="N/A", tags=['N', 'A']).to_dict())
            som_correct_paths_complete.append(som_correct_paths)
        print("corrected som:", som_correct_paths_complete)

        return som_correct_paths_complete
