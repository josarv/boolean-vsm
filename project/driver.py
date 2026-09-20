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
from pathlib import Path
from collections import defaultdict
from time import time

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

# anchor data paths to the repository root so the driver runs from anywhere
DATA_DIRECTORY = Path(__file__).resolve().parent.parent / "data"
document_directory = DATA_DIRECTORY / "documents"
queries_file = DATA_DIRECTORY / "queries.txt"
relevant_file = DATA_DIRECTORY / "relevant.txt"

def add_or_between_terms(query: str) -> str:
    return query.replace(" ", "||")
    # return ''.join("||" if char.isspace() else char for char in query)

# boolean

# glob files in the directory and index them
start = time()
document_count = 0
for filepath in glob(path.join(document_directory, "*")):
    if path.isfile(filepath):
        with open(filepath, "r") as file:
            content = file.read()
            filename = path.basename(filepath)
            boolean.index_document(filename, content)
            document_count += 1
if document_count == 0:
    raise SystemExit(f"No documents found in {document_directory}")
elapsed = time() - start
print(f"Indexing time (boolean/wall): {elapsed:.3f}s, {(elapsed / document_count):.4f}s avg over {document_count} documents")

start = time()
boolean_results = {}
with open(queries_file, "r") as file:
    for line in file:
        query = line.strip()
        if query:
            results = boolean.query(add_or_between_terms(query))
            boolean_results[query] = results
elapsed = time() - start
query_count = len(boolean_results)
print(f"Query time (boolean/wall): {elapsed:.3f}s, {(elapsed / query_count):.4f}s avg over {query_count} queries")

# for query in boolean_results:
#     print(f"Boolean results for query '{query}': {len(boolean_results[query])}")

# vsm

start = time()
collection = {}
for filepath in glob(path.join(document_directory, "*")):
    if path.isfile(filepath):
        with open(filepath, "r") as file:
            content = file.read()
            filename = path.basename(filepath)
            tokens = preprocess(content)
            collection[filename] = tokens
vsm.index_collection(collection)
elapsed = time() - start
print(f"Indexing time (vsm/wall): {elapsed:.3f}s, {(elapsed / len(collection)):.4f}s avg over {len(collection)} documents")

start = time()
vsm_results = {}
with open(queries_file, "r") as file:
    for line in file:
        query = line.strip()
        if query:
            results = vsm.query(query, top_k=100)
            vsm_results[query] = results
elapsed = time() - start
print(f"Query time (vsm/wall): {elapsed:.3f}s, {(elapsed / len(vsm_results)):.4f}s avg over {len(vsm_results)} queries")

# for query, result in vsm_results.items():
#     result = [document for document, score in result]
#     print(result)
#     # print(f"VSM results for query '{query}': {result}")

ground_truth = defaultdict(set)
with open(relevant_file, "r") as file:
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

def report(title: str, scores: list[tuple[str, float, float]]) -> None:
    print("=" * 50)
    print(title)
    print("=" * 50)
    for query, p, r in scores:
        print(f"Precision: {p:.3f}, Recall: {r:.3f}")
    mean_precision = sum(p for _, p, _ in scores) / len(scores)
    mean_recall = sum(r for _, _, r in scores) / len(scores)
    print("-" * 50)
    print(f"Mean precision: {mean_precision:.3f}, mean recall: {mean_recall:.3f}")

report("Boolean model", boolean_scores)

# evaluate vsm
vsm_scores = []
for idx, query in enumerate(vsm_results):
    retrieved = vsm_results[query]
    retrieved = [doc_id for doc_id, score in retrieved]
    relevant = ground_truth[idx]
    p = precision(retrieved, relevant)
    r = recall(retrieved, relevant)
    vsm_scores.append((query, p, r))

report("Vector space model", vsm_scores)
