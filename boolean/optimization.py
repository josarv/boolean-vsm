from .ast import ASTNode, ASTAndNode, ASTTrueNode, ASTOrNode, ASTFalseNode, ASTNotNode, ASTTermNode

def fold_constants(node: ASTNode) -> ASTNode:
    match node:
        case ASTAndNode(children=children):
            # recursively apply this transformation to all children
            transformed_children = [fold_constants(child) for child in children]
            # short circuit, if any child is FALSE, the whole AND expression is FALSE
            if any(isinstance(child, ASTFalseNode) for child in transformed_children):
                return ASTFalseNode()
            # drop all TRUE children (AND identity)
            filtered_children = [child for child in transformed_children if not isinstance(child, ASTTrueNode)]
            if not filtered_children:
                return ASTTrueNode()  # empty AND = True
            elif len(filtered_children) == 1:
                return filtered_children[0]  # AND with a single child = child
            else:
                return ASTAndNode(children=filtered_children)
        case ASTOrNode(children=children):
            transformed_children = [fold_constants(child) for child in children]
            if any(isinstance(child, ASTTrueNode) for child in transformed_children):
                return ASTTrueNode()
            filtered_children = [child for child in transformed_children if not isinstance(child, ASTFalseNode)]
            if not filtered_children:
                return ASTFalseNode()
            elif len(filtered_children) == 1:
                return filtered_children[0]
            else:
                return ASTOrNode(children=filtered_children)
        case ASTNotNode(child=child):
            transformed_child = fold_constants(child)
            # eliminate double negation
            if isinstance(transformed_child, ASTNotNode):
                return transformed_child.child
            # if the child is a constant, negate it
            if isinstance(transformed_child, ASTTrueNode):
                return ASTFalseNode()
            if isinstance(transformed_child, ASTFalseNode):
                return ASTTrueNode()
            return ASTNotNode(child=transformed_child)
        case ASTTrueNode() | ASTFalseNode() | ASTTermNode():
            return node
        case _:
            # fallback, return the node unchanged, or error out
            return node

def flatten_nested_operators(node: ASTNode) -> ASTNode:
    match node:
        case ASTAndNode(children=children):
            flattened_children = []
            for child in children:
                transformed_child = flatten_nested_operators(child)
                if isinstance(transformed_child, ASTAndNode):
                    flattened_children.extend(transformed_child.children)
                else:
                    flattened_children.append(transformed_child)
            return ASTAndNode(children=flattened_children)
        case ASTOrNode(children=children):
            flattened_children = []
            for child in children:
                transformed_child = flatten_nested_operators(child)
                if isinstance(transformed_child, ASTOrNode):
                    flattened_children.extend(transformed_child.children)
                else:
                    flattened_children.append(transformed_child)
            return ASTOrNode(children=flattened_children)
        case ASTNotNode(child=child):
            return ASTNotNode(child=flatten_nested_operators(child))
        case ASTTrueNode() | ASTFalseNode() | ASTTermNode():
            return node
        case _:
            return node


def deduplicate_operands(node: ASTNode) -> ASTNode:
    match node:
        case ASTAndNode() | ASTOrNode() as current_node:
            NodeType = type(current_node)
            transformed_children = [deduplicate_operands(child) for child in current_node.children]
            unique_children = []
            seen = set()
            for child in transformed_children:
                repr_child = repr(child)  # we use repr to identify unique nodes, structural equality
                if repr_child not in seen:
                    seen.add(repr_child)
                    unique_children.append(child)
            if not unique_children:
                return ASTTrueNode() if isinstance(current_node, ASTAndNode) else ASTFalseNode()  # identity
            elif len(unique_children) == 1:
                return unique_children[0]  # collapse single-child AND/OR
            else:
                return NodeType(children=unique_children)
        case ASTNotNode(child=child):
            return ASTNotNode(child=deduplicate_operands(child))
        case ASTTrueNode() | ASTFalseNode() | ASTTermNode():
            return node
        case _:
            return node

def simplify_tautologies_contradictions(node: ASTNode) -> ASTNode:
    match node:
        case ASTAndNode() | ASTOrNode() as current_node:
            NodeType = type(current_node)
            transformed_children = [simplify_tautologies_contradictions(child) for child in current_node.children]
            # collapse empty or singleton children
            if not transformed_children:
                return ASTTrueNode() if isinstance(current_node, ASTAndNode) else ASTFalseNode()  # identity
            elif len(transformed_children) == 1:
                return transformed_children[0]
            # detect contradictions/tautologies
            child_reprs = {repr(child): child for child in transformed_children}  # once again, using repr for structural equality
            for child in transformed_children:
                if isinstance(child, ASTNotNode) and repr(child.child) in child_reprs:
                    # found a pair: x and !! x
                    return ASTFalseNode() if isinstance(child, ASTAndNode) else ASTTrueNode()
                    # if operand is and: a && !!a = false
                    # if operand is or: a || !!a = true
            return NodeType(children=transformed_children)
        case ASTNotNode(child=child):
            return ASTNotNode(child=simplify_tautologies_contradictions(child))
        case ASTTrueNode() | ASTFalseNode() | ASTTermNode():
            return node
        case _:
            return node
