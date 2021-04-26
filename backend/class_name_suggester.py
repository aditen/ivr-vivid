from typing import List
import gensim.downloader as api


class ClassNameSuggester:
    def __init__(self):
        # TODO: load correct gensim model, order vocab by frequency, build reverse dict: top 20 most similar words -> class
        # see https://radimrehurek.com/gensim/auto_examples/howtos/run_downloader_api.html
        self.model = api.load("glove-wiki-gigaword-50")

    # TODO: predict nearest classes
    def predict_class(self, query: str) -> List[str]:
        similar = []
        try:
            similar = similar + [x[0] for x in self.model.most_similar(query)]
        except KeyError:
            print("key error")
        return similar
