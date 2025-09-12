from project.preprocess import tokenize, remove_stopwords
from boolean.utility import compose
from boolean.model import BooleanIRModel
from vsm.model import VSM

from glob import glob
from os import path


preprocess = compose(
    tokenize,
    remove_stopwords
)

boolean = BooleanIRModel(preprocessing_pipeline=preprocess)
vsm = VSM(preprocessing_pipeline=preprocess)

document_directory = "../data/documents"

def add_or_between_terms(query: str) -> str:
    return ''.join(" || " if char.isspace() else char for char in query)

# boolean

# glob files in the directory and index them
for filepath in glob(path.join(document_directory, "*")):
    if path.isfile(filepath):
        with open(filepath, "r") as file:
            content = file.read()
            filename = path.basename(filepath)
            boolean.index_document(filename, content)

boolean_results = {}
with open("../data/queries.txt", "r") as file:
    for line in file:
        query = line.strip()
        if query:
            results = boolean.query(add_or_between_terms(query))
            boolean_results[query] = results

# for query in boolean_results:
#     print(f"Boolean results for query '{query}': {boolean_results[query]}")

# vsm

collection = {}
for filepath in glob(path.join(document_directory, "*")):
    if path.isfile(filepath):
        with open(filepath, "r") as file:
            content = file.read()
            filename = path.basename(filepath)
            tokens = preprocess(content)
            collection[filename] = tokens
vsm.index_collection(collection)

vsm_results = {}
with open("../data/queries.txt", "r") as file:
    for line in file:
        query = line.strip()
        if query:
            results = vsm.query(query, top_k=10)
            vsm_results[query] = results

# for query, result in vsm_results.items():
#     result = [document for document, score in result]
#     print(result)
#     # print(f"VSM results for query '{query}': {result}")

