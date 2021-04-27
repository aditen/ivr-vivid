from typing import List

from data_classes import FilterCriteria


class QueryHandler:
    def __init__(self):
        print("Initialized query handle")

    def handle_query(self, filter_criteria: FilterCriteria) -> List[List[str]]:
        # 1: Laura filters the keyframes
        # 2: Baris does the SOM on the keyframes
        # 3: Adrian gets the response and displays it on the GUI
        print(self)
        print(filter_criteria.text)
        return [["test"]]
