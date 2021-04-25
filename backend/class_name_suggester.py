from typing import List


class ClassNameSuggester:
    def __init__(self):
        # TODO: load gensim model, order vocab by frequency
        pass

    # TODO: predict nearest classes
    def predict_class(self, query: str) -> List[str]:
        if query is None or query == "":
            return []
        return ["heterotroph", "cell"]
