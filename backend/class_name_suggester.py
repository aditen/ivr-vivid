from typing import List
import gensim.downloader as api
import pandas as pd
import operator

class ClassNameSuggester:
    def __init__(self):
        # TODO: load correct gensim model, order vocab by frequency, build reverse dict: top 20 most similar words -> class
        # see https://radimrehurek.com/gensim/auto_examples/howtos/run_downloader_api.html
        self.model = api.load("glove-wiki-gigaword-50")

    # TODO: predict nearest classes
    def predict_class(self, query: str) -> List[str]:
        nasnet = pd.read_csv('/home/jonaslaura/Documents/ivr-vivid-main/backend/features_data/nasnet_formated.csv')
        nasnetclasses = nasnet['class'].unique()
        similar = []
        try:
            #similar = similar + [x[0] for x in self.model.most_similar(query)]
            #print(similar)
            word_to_query = query
            distances_to_word = {}
            for x in nasnetclasses:
                if x in self.model:
                    distances_to_word[x] = self.model.similarity(word_to_query, x)
            res = sorted(distances_to_word.items(), key = operator.itemgetter(1), reverse = True)[:10]
            similar = list(list(zip(*res))[0])
            print(similar)
        except KeyError:
            print("key error")
        return similar

