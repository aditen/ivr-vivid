from typing import List
from PIL import Image
import numpy as np
from xpysom import XPySom
from sklearn.preprocessing import StandardScaler
from data_classes import FilterCriteria


class QueryHandler:
    def __init__(self):
        print("Initialized query handler")

    def find_index_from_image(img, image_data):  # this function finds the index of the image within the image_data
        for index in range(len(image_data)):
            if (np.array_equal(image_data[index], img)):
                return index

    def produce_SOM_grid(shot_locations, grid_w, grid_h, it=10):
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
                position_grid[position] = QueryHandler.find_index_from_image(img,
                                                                image_data)  # we simply put to the grid the one that we encounter first for the position
            else:
                to_fill.append(
                    i)  # in the win_map, some positions are not filled, so the win_map did not put any image to a position so we put the index of those positions in the to_fill(not the positions but their index i for the grid[i] (handled by the grid structure)
        collided = collided[::-1]
        for i in to_fill:
            img = collided.pop()
            position = np.unravel_index(i, (grid_h, grid_w))
            index = QueryHandler.find_index_from_image(img, image_data)
            position_grid[
                position] = index  # for the places that are not filled by the win_map, we put the collided images in order

        location_grid = np.take(shot_locations, position_grid)
        return location_grid

    def handle_query(self, filter_criteria: FilterCriteria, shot_locations, grid_h, grid_w, it) -> List[List[str]]:
        # 1: Laura filters the keyframes
        # 2: Baris does the SOM on the keyframes
        SOM_shot_locations=QueryHandler.produce_SOM_grid(shot_locations, grid_w, grid_h, it)
        # 3: Adrian gets the response and displays it on the GUI
        #print(self)
        print(filter_criteria)
        all_kf_test = ["https://iten.engineering/files/keyframes/00032/shot00032_" +
                       str(i) + "_RKF.png" for i in range(1, 33)]
        result_mat = []
        count = 0
        while count < len(all_kf_test):
            result_mat.append(all_kf_test[count:(count + filter_criteria.gridWidth)])
            count += filter_criteria.gridWidth
        return result_mat
