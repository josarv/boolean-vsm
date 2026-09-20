from boolean.parser import RecursiveDescentParser, preserve_boolean_operators
from boolean.optimization import (
    fold_constants,
    flatten_nested_operators,
    deduplicate_operands,
    simplify_tautologies_contradictions,
    optimize,
)
from project.preprocess import tokenize

parser = RecursiveDescentParser()

query_pipeline = preserve_boolean_operators(tokenize)

def display_query_processing(query_string: str):
    print(f"1. Original Query: {query_string}")
    processed_query = query_pipeline(query_string)
    print(f"2. Processed Query: {processed_query}")
    ast = parser.parse(processed_query)
    print("3. AST:", ast)
    ast.root = fold_constants(ast.root)
    print("4. Folded AST:", ast)
    ast.root = flatten_nested_operators(ast.root)
    print("5. Flattened AST:", ast)
    ast.root = deduplicate_operands(ast.root)
    print("6. Deduplicated AST:", ast)
    ast.root = simplify_tautologies_contradictions(ast.root)
    print("7. Simplified AST:", ast)
    # the passes above run once each; optimize repeats them until the tree
    # settles, which is what the model actually uses
    ast.root = optimize(ast.root)
    print("8. Fully optimized AST:", ast)
    print("-" * 50)

queries = [
    # Original -> after all passes
    ("#true && a", "a"),
    ("#false || b", "b"),
    ("a && #false", "#false"),
    ("b || #true", "#true"),
    ("!!!!c", "c"),
    ("!!#true", "#false"),
    ("!!!!#false", "#false"),
    ("#true && #false", "#false"),
    ("!!!!((d || #true))", "#true"),

    # Flattening nested operators
    ("((a && ((b && c))))", "a && b && c"),
    ("((x || ((y || z))))", "(x || y || z)"),
    ("((p && ((q && ((r && s))))))", "(p && q && r && s)"),
    ("!!((a && ((b && c))))", "!!(a && b && c)"),
    ("((m || ((n || ((o || p))))))", "(m || n || o || p)"),

    # Deduplication
    ("((a && a))", "a"),
    ("((b || b || c))", "(b || c)"),
    ("((x && y && x))", "(x && y)"),
    ("((p || q || q || p))", "(p || q)"),
    ("((a && b && a && c))", "(a && b && c)"),

    # Tautologies / contradictions
    ("((a && !!a))", "#false"),
    ("((b || !!b))", "#true"),
    ("((x && y && !!y))", "#false"),
    ("((p || q || !!q))", "#true"),
    ("((m && n && !!m))", "#false"),
    ("((r || s || !!r))", "#true"),
    ("((a && b && !!c))", "(a && b && !c)"),
    ("((x || y || !!z))", "(x || y || !z)"),

    # Combined transformations
    ("#true && ((a && #true))", "a"),
    ("((b || #false || b))", "b"),
    ("((c && ((d && #false))))", "#false"),
    ("((x || ((y || #true))))", "#true"),
    ("((p && !!p))", "#false"),
    ("((q || !!q || r))", "#true"),
    ("((a && !!a && b))", "#false"),
    ("((m || n || !!n))", "#true"),

    # only reducible by repeating the passes (see optimize)
    ("a && ((b || !!b))", "a"),
    ("a || ((b && !!b))", "a"),
    ("a || (( ))", "a"),
    ("a && (( )) && b", "(a && b)"),
]

for query, expected in queries:
    print("Expected Result:", expected)
    display_query_processing(query)
