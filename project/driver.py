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

# def add_or_between_terms(query: str) -> str:
#     return ''.join(" || " if char.isspace() else char for char in query)
#
# # glob files in the directory and index them
# for filepath in glob(path.join(document_directory, "*")):
#     if path.isfile(filepath):
#         with open(filepath, "r") as file:
#             content = file.read()
#             filename = path.basename(filepath)
#             boolean.index_document(filename, content)

# same for vsm
collection = {}
for filepath in glob(path.join(document_directory, "*")):
    if path.isfile(filepath):
        with open(filepath, "r") as file:
            content = file.read()
            filename = path.basename(filepath)
            tokens = preprocess(content)
            collection[filename] = tokens
vsm.index_collection(collection)

print(vsm.pretty_query("Are there abnormalities of taste in CF patients"))
