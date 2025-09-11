from project.preprocess import tokenize, remove_stopwords
from boolean.utility import compose
from boolean.model import BooleanIRModel

from glob import glob
from os import path


preprocess = compose(
    tokenize,
    remove_stopwords
)

boolean = BooleanIRModel(preprocessing_pipeline=preprocess)

document_directory = "../data/documents"

# glob files in the directory and index them
for filepath in glob(path.join(document_directory, "*")):
    if path.isfile(filepath):
        with open(filepath, "r") as file:
            content = file.read()
            filename = path.basename(filepath)
            boolean.index_document(filename, content)

print(boolean.pretty_query(''.join(" || " if char.isspace() else char for char in "pseudomonas aeruginosa")))
