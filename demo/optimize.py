from boolean.optimization import fold_constants, flatten_nested_operators, deduplicate_operands, simplify_tautologies_contradictions
from boolean.parser import RecursiveDescentParser

parser = RecursiveDescentParser()

def optimize_and_print_ast(query: str, parser):
    print(f"Original Query: {query}")
    ast = parser.parse(query)
    print("1. Original AST:", ast)

    ast.root = fold_constants(ast.root)
    print("2. Folded AST:", ast)

    ast.root = flatten_nested_operators(ast.root)
    print("3. Flattened AST:", ast)

    ast.root = deduplicate_operands(ast.root)
    print("4. Deduplicated AST:", ast)

    ast.root = simplify_tautologies_contradictions(ast.root)
    print("5. Simplified AST:", ast)
    print("=" * 50)


# for these next 4, we can commend out lines 15 and downward in fold_and_print_ast
# --- Use Case 1: AND Simplification ---
# optimize_and_print_ast("cat && #false && dog", parser)
# optimize_and_print_ast("cat && #true && dog", parser)
# optimize_and_print_ast("#true && #true", parser)
#
# # --- Use Case 2: OR Simplification ---
# optimize_and_print_ast("cat || #true || dog", parser)
# optimize_and_print_ast("cat || #false || dog", parser)
# optimize_and_print_ast("#false || #false", parser)
#
# # --- Use Case 3: NOT Simplification ---
# optimize_and_print_ast("!! cat", parser)
# optimize_and_print_ast("!! #true", parser)
# optimize_and_print_ast("!! #false", parser)
#
# # --- Use Case 4: Nested and Mixed Operations ---
# optimize_and_print_ast("((cat && #false)) || #true", parser)
# optimize_and_print_ast("!! #true && (dog || #true)", parser)
# optimize_and_print_ast("!! cat && #false", parser)

# Test cases for flattening AND and OR
# optimize_and_print_ast("cat && ((dog && mouse))", parser)
# optimize_and_print_ast("cat || ((dog || mouse))", parser)
# optimize_and_print_ast("((((cat || dog)) || ((mouse || rabbit))))", parser)
#
# # Test cases for combining both optimization passes
# optimize_and_print_ast("((cat && #true)) && ((dog && #false))", parser)
# optimize_and_print_ast("((!! ((!! cat)))) && ((dog || #false))", parser)
# optimize_and_print_ast("(( ((!! #true)) || ((cat && ((dog || mouse)) )) ))", parser)

# Test cases for deduplication
# optimize_and_print_ast("cat && cat && dog", parser)
# optimize_and_print_ast("cat || dog || cat", parser)
# optimize_and_print_ast("(cat && dog) || (cat && dog)", parser)
#
# # Test case for the full optimization pipeline
# optimize_and_print_ast("(cat && #true) || (cat && #true)", parser)

optimize_and_print_ast("cat && !!cat", parser)
