from utils import get_terms

class Query:
    def __init__(self, query_text):
        self.text = query_text
        self.terms = get_terms(self.text)
        self.tf = {}
        for term in self.terms:
            if term not in self.tf:
                self.tf[term] = 0
            self.tf[term] += 1

    def get_terms(self):
        return list(self.tf.keys())

    def get_tf(self):
        return list(self.tf.values())