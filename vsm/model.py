class VSM:
    def __init__(self):
        pass

    def index_collection(self):
        pass

    def query(self, query_string: str) -> list[tuple[str, float]]:
        pass
        # compute query vector
        # compute cosine similarities
        # return ranked list of (filename, score) using self.index.postings_to_filenames
