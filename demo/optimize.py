from boolean.optimization import fold_constants
from boolean.parser import RecursiveDescentParser

parser = RecursiveDescentParser()

def fold_and_print_ast(query: str, parser):
    print(f"Original Query: {query}")
    ast = parser.parse(query)
    print("Original AST:", ast)

    ast.root = fold_constants(ast.root)
    print("Folded AST:", ast)
    print("-" * 50)

# --- Use Case 1: AND Simplification ---
fold_and_print_ast("cat && #false && dog", parser)
fold_and_print_ast("cat && #true && dog", parser)
fold_and_print_ast("#true && #true", parser)

# --- Use Case 2: OR Simplification ---
fold_and_print_ast("cat || #true || dog", parser)
fold_and_print_ast("cat || #false || dog", parser)
fold_and_print_ast("#false || #false", parser)

# --- Use Case 3: NOT Simplification ---
fold_and_print_ast("!! cat", parser)
fold_and_print_ast("!! #true", parser)
fold_and_print_ast("!! #false", parser)

# --- Use Case 4: Nested and Mixed Operations ---
fold_and_print_ast("((cat && #false)) || #true", parser)
fold_and_print_ast("!! #true && (dog || #true)", parser)
fold_and_print_ast("!! cat && #false", parser)
