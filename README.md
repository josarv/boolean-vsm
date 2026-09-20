# Boolean and VSM IR Implementation

Python implementation of the Boolean and Vector Space models, build from scratch, as part of an Information Retrieval Course.
Both use the same preprocessing pipeline and were evaluated against the same test collection.

The point of this educational project was to implement the retrieval machinery directly rather than
call into an existing IR library: the inverted index, the query parser, the query
optimizer and the scoring are all hand written. The only third party dependency is NLTK,
used for tokenization, POS tagging and lemmatization.

## What is implemented

### The preprocessing pipeline

Consists of compasable stages and is applied identically to both documents and queries.
Its stages are: tokenization, lowercasing, stopword removal, Penn Treebank POS tagging, mapping of those tags to WordNet Tagas, POS aware lemmatization and synonym normalization that maps each term to the first lemma of its first WordNet synset.

### Boolean model (`boolean/`)

- An inverted index with pluggable posting list implementations, behind a `Protocol`.
  Documents get integer IDs and postings are sets
- A recursive descent parser for the query grammar below, producing an AST
- Four AST optimization passes: constant folding and double negation elimination,
  flattening of nested same operator nodes, operand deduplication, and
  tautology/contradiction detection (`a && !!a` → false, `a || !!a` → true)
- Short circuiting evaluation: an AND stops once the running result is empty, an OR
  stops once it covers the whole collection

The query grammar uses doubled operators so that single characters appearing in ordinary
text are not mistaken for syntax:

### Vector space model (`vsm/`) 

Tf-idf weighting with cosine similarity, precomputed document norms, and top-k ranked retrieval.

### Evaluation** (`project/driver.py`)

Indexes the collection with both models, runs the 20 test queries and reports per query and mean precision and recall against the
relevance judgments.

## Running

Requires Python 3.12+. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m project.driver
```

## Results

Because the test queries are natural language, the driver joins their terms with `||`
before handing them to the Boolean model. That gives the Boolean model high recall and
very low precision, which is the expected weakness of set based retrieval without
ranking. The vector space model trades recall for a threefold improvement in precision.

| Model                    | Mean precision | Mean recall |
| ------------------------ | -------------- | ----------- |
| Boolean                  | 0.040          | 0.896       |
| Vector space (top k=100) | 0.131          | 0.437       |
