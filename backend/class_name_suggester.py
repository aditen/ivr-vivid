import operator
import os
import re
from typing import List

import gensim.downloader as api
import pandas as pd


class ClassNameSuggester:
    def __init__(self):
        # see https://radimrehurek.com/gensim/auto_examples/howtos/run_downloader_api.html
        self.model = api.load("glove-wiki-gigaword-50")
        self.nasnet = pd.read_csv(os.getenv(key="PREDICTIONS_ROOT",
                                            default='C:/Users/41789/Documents/uni/fs21/video_retrieval/') + 'nasnet_formated.csv')
        print("Initialized class name suggester")

    def predict_class(self, query: str) -> List[str]:
        if query not in self.model.key_to_index:
            return []
        nasnetclasses = self.nasnet['class'].unique()
        word_to_query = query
        distances_to_word = {}
        for x in nasnetclasses:
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
        return similar #[s.replace("_", " ") for s in similar]
