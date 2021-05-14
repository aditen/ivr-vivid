import operator
import os
import re
from typing import List

import gensim.downloader as api
import mariadb

class ClassNameSuggester:
    def __init__(self):
        # see https://radimrehurek.com/gensim/auto_examples/howtos/run_downloader_api.html
        self.model = api.load("glove-wiki-gigaword-50")
        # SELECT DISTINCT class from nasnet_classification nc where confidence > 0.5
        self.db_connection = mariadb.connect(user=os.getenv("db_user"), password=os.getenv("db_pw"),
                                             database=os.getenv("db_name"), host=os.getenv("db_host"), port=3306)
        self.db_connection.auto_reconnect = True
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT DISTINCT class from nasnet_classification nc where confidence > 0.5")
        sql_result = cursor.fetchall()
        self.all_classes = [tup[0] for tup in sql_result]
        cursor.close()
        self.db_connection.close()
        print("Initialized class name suggester")

    def predict_class(self, query: str) -> List[str]:
        if query not in self.model.key_to_index:
            return []
        word_to_query = query
        distances_to_word = {}
        for x in self.all_classes:
            if x in self.model.key_to_index:
                distances_to_word[x] = self.model.similarity(word_to_query, x)
            else:
                best_candidate = float("-inf")
                for candidate in re.split("_|-", x):
                    if candidate in self.model.key_to_index:
                        sim_candidate = self.model.similarity(word_to_query, candidate)
                        if sim_candidate > best_candidate:
                            distances_to_word[x] = sim_candidate
                            best_candidate = sim_candidate
        res = sorted(distances_to_word.items(), key=operator.itemgetter(1), reverse=True)[:10]
        similar = list(list(zip(*res))[0])
        return similar
