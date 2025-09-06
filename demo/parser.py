from boolean.parser import RecursiveDescentParser, preserve_boolean_operators
from project.preprocess import compose, tokenize, lowercase, remove_punctuation_tokens, add_penn_treebank_tags, convert_penn_treebank_to_wordnet_tags, lemmatize, strip_pos_tags, remove_stopwords

def print_ast(query: str, parser: RecursiveDescentParser):
    print(f"Query: {query}")
    ast = parser.parse(query)
    print("AST:", ast)
    print("-" * 50)


parser = RecursiveDescentParser()
queries = [
    "cat && dog",
    "cat || dog && mouse",
    "!! cat",
    "(( cat || dog )) && mouse",
    "true && false",  # should treat 'true' and 'false' as terms
    "#true || #false",  # logical constants
    "cat && #true || false",  # mix of term, constant, and term
    "!! #false && (dog || #true)",
    "",  # empty query
    "!!",  # dangling NOT
]

# for query in queries:
#     print_ast(query, parser)

preprocessing_pipeline = compose(
    # expand_contractions,
    tokenize,
    lowercase,
    remove_punctuation_tokens,
    # remove_digit_tokens,
    # remove_too_short_tokens,
    add_penn_treebank_tags,
    convert_penn_treebank_to_wordnet_tags,
    lemmatize,
    # map_to_synonyms,
    strip_pos_tags,
    remove_stopwords,
)

query_pipeline = preserve_boolean_operators(preprocessing_pipeline)

more_queries = [
    "Cat && Dog",
    "  Cat  ||  Dog && Mouse ",
    "!! Cat",
    "(( Cat || Dog )) && Mouse",
    "#true && #false",
    "  Cat && #true || False  ",
    "!! #false && (Dog || #true)"
]

for query in more_queries:
    processed = query_pipeline(query)
    print(f"Original: {query}")
    print(f"Processed: {processed}")
    print("-" * 50)
