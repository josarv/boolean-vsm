from project.preprocess import (
    tokenize,
    lowercase,
    remove_stopwords,
    add_penn_treebank_tags,
    convert_penn_treebank_to_wordnet_tags,
    lemmatize,
    map_to_synonyms,
    strip_pos_tags
)
from boolean.utility import compose
from boolean.model import BooleanIRModel
from vsm.model import VSM

from glob import glob
from os import path
from collections import defaultdict

preprocess = compose(
    tokenize,
    lowercase,
    remove_stopwords,
    add_penn_treebank_tags,
    convert_penn_treebank_to_wordnet_tags,
    lemmatize,
    map_to_synonyms,
    strip_pos_tags
)

boolean = BooleanIRModel(preprocessing_pipeline=preprocess)
vsm = VSM(preprocessing_pipeline=preprocess)

document_directory = "../data/documents"

def add_or_between_terms(query: str) -> str:
    return query.replace(" ", "||")
    # return ''.join("||" if char.isspace() else char for char in query)

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
#     print(f"Boolean results for query '{query}': {len(boolean_results[query])}")


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
            results = vsm.query(query, top_k=100)
            vsm_results[query] = results

# for query, result in vsm_results.items():
#     result = [document for document, score in result]
#     print(result)
#     # print(f"VSM results for query '{query}': {result}")

ground_truth = defaultdict(set)
with open("../data/relevant.txt", "r") as file:
    for query_no, line in enumerate(file):
        ids = line.strip().split()
        padded_ids = {doc_id.zfill(5) for doc_id in ids}
        ground_truth[query_no] = padded_ids

def precision(retrieved: list[str], relevant: set[str]) -> float:
    if not retrieved:
        return 0.0
    return len(set(retrieved) & relevant) / len(retrieved)

def recall(retrieved: list[str], relevant: set[str]) -> float:
    if not relevant:
        return 0.0
    return len(set(retrieved) & relevant) / len(relevant)

# evaluate boolean
boolean_scores = []
for idx, query in enumerate(boolean_results):
    retrieved = boolean_results[query]
    relevant = ground_truth[idx]
    p = precision(retrieved, relevant)
    r = recall(retrieved, relevant)
    boolean_scores.append((query, p, r))

print("=" * 50)
print("Boolean model")
print("=" * 50)
for query, p, r in boolean_scores:
    # print(f"Query: {query} | Precision: {p:.3f}, Recall: {r:.3f}")
    print(f"Precision: {p:.3f}, Recall: {r:.3f}")

# # evaluate vsm
vsm_scores = []
for idx, query in enumerate(vsm_results):
    retrieved = vsm_results[query]
    retrieved = [doc_id for doc_id, score in retrieved]
    relevant = ground_truth[idx]
    p = precision(retrieved, relevant)
    p = precision(retrieved, relevant)
    r = recall(retrieved, relevant)
    vsm_scores.append((query, p, r))

print("=" * 50)
print("Vector space model")
print("=" * 50)
for query, p, r in vsm_scores:
    # print(f"Query: {query} | Precision: {p:.3f}, Recall: {r:.3f}")
    print(f"Precision: {p:.3f}, Recall: {r:.3f}")
