from typing import List

from data_classes import FilterCriteria


class QueryHandler:
    def __init__(self):
        print("Initialized query handler")

    def handle_query(self, filter_criteria: FilterCriteria) -> List[List[str]]:
        # 1: Laura filters the keyframes
        # 2: Baris does the SOM on the keyframes
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
