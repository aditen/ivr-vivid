from typing import List
import gensim.downloader as api

class ClassNameSuggester:
    def __init__(self):
        # TODO: load correct gensim model, order vocab by frequency
        # see https://radimrehurek.com/gensim/auto_examples/howtos/run_downloader_api.html
        self.model = api.load("glove-wiki-gigaword-50")

    # TODO: predict nearest classes
    def predict_class(self, query: str) -> List[str]:
        if query is None or query == "":
            return []
        print(self.model.most_similar(query))
        return ["heterotroph", "cell"]
