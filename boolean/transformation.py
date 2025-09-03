from .ast import ASTNode, ASTAndNode, ASTTrueNode, ASTOrNode, ASTFalseNode, ASTNotNode, ASTTermNode


class Transformer:
    def transform(self, node: ASTNode) -> ASTNode:
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node: ASTNode) -> ASTNode:
        return node

# This (Negation Normal Form) transformer does:
# flattening and: (A AND (B AND C)) -> AND(A, B, C)
# flattening or: (A OR (B OR C)) -> OR(A, B, C)
# double negation elimination -> NOT(NOT(A)) -> A
# De morgan: NOT(A AND B) -> OR(NOT(A), NOT(B))
# De morgan: NOT(A OR B) -> AND(NOT(A), NOT(B))
class NNFTransformer(Transformer):
    def visit_ASTAndNode(self, node: ASTAndNode) -> ASTNode:
        # transform children
        children = [self.transform(child) for child in node.children]

        # flatten nested AND nodes
        flattened_children = []
        for child in children:
            if isinstance(child, ASTAndNode):
                flattened_children.extend(child.children)
            else:
                flattened_children.append(child)

        # remove duplicate children
        # we could do unique_children = list(set(flattened_children)
        # BUT it won't work as ASTTermNode('a') and another ASTTermNode('a')
        # are seen as different objects, so set sees them as different
        # for this to work, we need ASTNodes to implement __hash__ and __eq__
        # even then, ASTAndNode contains lists which are unhashable
        # therefore:
        seen = set()
        unique_children = []
        for flat_child in flattened_children:
            key = repr(flat_child)
            if key not in seen:
                seen.add(key)
                unique_children.append(flat_child)

        # handle special cases
        if not unique_children:
            return ASTTrueNode()
        if len(unique_children) == 1:
            return unique_children[0]
        return ASTAndNode(unique_children)

    def visit_ASTOrNode(self, node: ASTOrNode) -> ASTNode:
        # transform children
        children = [self.transform(child) for child in node.children]

        # flatten nested OR nodes
        flattened_children = []
        for child in children:
            if isinstance(child, ASTOrNode):
                flattened_children.extend(child.children)
            else:
                flattened_children.append(child)

        # remove duplicates (same as above)
        seen = set()
        unique_children = []
        for flat_child in flattened_children:
            key = repr(flat_child)
            if key not in seen:
                seen.add(key)
                unique_children.append(flat_child)

        # handle special cases
        if not unique_children:
            return ASTFalseNode()
        if len(unique_children) == 1:
            return unique_children[0]

        return ASTOrNode(unique_children)

    def visit_ASTNotNode(self, node: ASTNotNode) -> ASTNode:
        child = self.transform(node.child)

        # NOT(NOT(A)) -> A
        if isinstance(child, ASTNotNode):
            return self.transform(child.child)

        # De Morgan: NOT(AND(...)) -> OR(NOT(...))
        if isinstance(child, ASTAndNode):
            return ASTOrNode([self.transform(ASTNotNode(child)) for child in child.children])

        # De Morgan: NOT(OR(...)) -> AND(NOT(...))
        if isinstance(child, ASTOrNode):
            return ASTAndNode([self.transform(ASTNotNode(child)) for child in child.children])

        return ASTNotNode(child)

    def visit_ASTTermNode(self, node: ASTTermNode) -> ASTNode:
        return node

    def visit_ASTTrueNode(self, node: ASTTrueNode) -> ASTNode:
        return node

    def visit_ASTFalseNode(self, node: ASTFalseNode) -> ASTNode:
        return node

# This (Conjuctive Normal Form) transformer REQUIRES NNF transformed tree and:
# distributes or over and: A OR (B AND C) -> (A OR B) AND (A OR C)
class CNFTransformer(Transformer):
    def visit_ASTAndNode(self, node: ASTAndNode) -> ASTNode:
        # transform children
        children = [self.transform(child) for child in node.children]
        return ASTAndNode(children)

    def visit_ASTOrNode(self, node: ASTOrNode) -> ASTNode:
        # transform children
        children = [self.transform(child) for child in node.children]

        # if a child is and, distribute or over it
        for i, child in enumerate(children):
            if isinstance(child, ASTAndNode):
                # remove the and child
                remaining = children[:i] + children [i + 1:]
                # distribute or over each child of and
                distributed = [ASTOrNode([child] + remaining) for child in child.children]
                # recursively transform the new and node
                return self.transform(ASTAndNode(distributed))

        if len(children) == 1:
            return children[0]
        return ASTOrNode(children)

    def visit_ASTNotNode(self, node: ASTNotNode) -> ASTNode:
        return node

    def visit_ASTTermNode(self, node: ASTTermNode) -> ASTNode:
        return node

    def visit_ASTTrueNode(self, node: ASTTrueNode) -> ASTNode:
        return node

    def visit_ASTFalseNode(self, node: ASTFalseNode) -> ASTNode:
        return node

class Simplifier(Transformer):
    def visit_ASTAndNode(self, node: ASTAndNode) -> ASTNode:
        # transform children
        children = [self.transform(child) for child in node.children]

        # flatten nested ands and remove duplicates
        flattened_children = []
        seen = set()
        for child in children:
            if isinstance(child, ASTAndNode):
                for grandchild in child.children:
                    key = repr(grandchild)
                    if key not in seen:
                        seen.add(key)
                        flattened_children.append(grandchild)
            else:
                key = repr(child)
                if key not in seen:
                    seen.add(key)
                    flattened_children.append(child)

        # constant folding
        if any(isinstance(child, ASTFalseNode) for child in flattened_children):
            return ASTFalseNode()
        flattened_children = [child for child in flattened_children if not isinstance(child, ASTTrueNode)]
        if not flattened_children:
            return ASTTrueNode()
        if len(flattened_children) == 1:
            return flattened_children[0]

        # absorption
        result_children = []
        for child in flattened_children:
            if isinstance(child, ASTOrNode):
                or_terms = {repr(term_child) for term_child in child.children}
                flattened_terms = {repr(flat_child) for flat_child in flattened_children}
                if flattened_terms & or_terms:
                    continue  # absorbed
            result_children.append(child)
        return ASTAndNode(result_children)

    def visit_ASTOrNode(self, node: ASTOrNode) -> ASTNode:
        # transform children
        children = [self.transform(child) for child in node.children]

        # flatten nested ors and remove duplicates
        flattened_children = []
        seen = set()
        for child in children:
            if isinstance(child, ASTOrNode):
                for grandchild in child.children:
                    key = repr(grandchild)
                    if key not in seen:
                        seen.add(key)
                        flattened_children.append(grandchild)
            else:
                key = repr(child)
                if key not in seen:
                    seen.add(key)
                    flattened_children.append(child)

        # constant folding
        if any(isinstance(child, ASTTrueNode) for child in flattened_children):
            return ASTTrueNode()
        flattened_children = [child for child in flattened_children if not isinstance(child, ASTFalseNode)]
        if not flattened_children:
            return ASTFalseNode()
        if len(flattened_children) == 1:
            return flattened_children[0]

        # absorption
        result_children = []
        for child in flattened_children:
            if isinstance(child, ASTAndNode):
                and_terms = {repr(term_child) for term_child in child.children}
                flattened_terms = {repr(flat_child) for flat_child in flattened_children}
                if flattened_terms & and_terms:
                    continue  # absorbed
            result_children.append(child)
        return ASTOrNode(result_children)

    def visit_ASTNotNode(self, node: ASTNotNode) -> ASTNode:
        # transform child
        child = self.transform(node.child)

        # double negation elimination
        if isinstance(child, ASTNotNode):
            return self.transform(child.child)
        return ASTNotNode(child)

    def visit_ASTTermNode(self, node: ASTTermNode) -> ASTNode:
        return node

    def visit_ASTTrueNode(self, node: ASTTrueNode) -> ASTNode:
        return node

    def visit_ASTFalseNode(self, node: ASTFalseNode) -> ASTNode:
        return node

    class RobustSimplifier(Transformer):
        """
        Safely simplifies an AST, handling edge cases:
        - Flatten AND/OR nodes
        - Remove duplicates
        - Fold constants
        - Handle absorption carefully
        - Replace empty AND/OR with TRUE/FALSE
        """

        def visit_ASTAndNode(self, node: ASTAndNode) -> ASTNode:
            children = [self.transform(c) for c in node.children]

            # Flatten nested ANDs and remove duplicates
            flattened = []
            seen = set()
            for c in children:
                if isinstance(c, ASTAndNode):
                    for gc in c.children:
                        key = repr(gc)
                        if key not in seen:
                            seen.add(key)
                            flattened.append(gc)
                else:
                    key = repr(c)
                    if key not in seen:
                        seen.add(key)
                        flattened.append(c)

            # Constant folding
            if any(isinstance(c, ASTFalseNode) for c in flattened):
                return ASTFalseNode()
            flattened = [c for c in flattened if not isinstance(c, ASTTrueNode)]
            if not flattened:
                return ASTTrueNode()
            if len(flattened) == 1:
                return flattened[0]

            # Absorption: remove OR children that are redundant
            result_children = []
            for c in flattened:
                if isinstance(c, ASTOrNode):
                    or_terms = {repr(tc) for tc in c.children}
                    flattened_terms = {repr(fc) for fc in flattened if fc is not c}
                    if or_terms & flattened_terms:
                        # Only skip if other terms exist, never remove last child
                        if len(flattened) > 1:
                            continue
                result_children.append(c)

            if not result_children:
                return ASTTrueNode()
            if len(result_children) == 1:
                return result_children[0]

            return ASTAndNode(result_children)

        def visit_ASTOrNode(self, node: ASTOrNode) -> ASTNode:
            children = [self.transform(c) for c in node.children]

            # Flatten nested ORs and remove duplicates
            flattened = []
            seen = set()
            for c in children:
                if isinstance(c, ASTOrNode):
                    for gc in c.children:
                        key = repr(gc)
                        if key not in seen:
                            seen.add(key)
                            flattened.append(gc)
                else:
                    key = repr(c)
                    if key not in seen:
                        seen.add(key)
                        flattened.append(c)

            # Constant folding
            if any(isinstance(c, ASTTrueNode) for c in flattened):
                return ASTTrueNode()
            flattened = [c for c in flattened if not isinstance(c, ASTFalseNode)]
            if not flattened:
                return ASTFalseNode()
            if len(flattened) == 1:
                return flattened[0]

            # Absorption: remove AND children that are redundant
            result_children = []
            for c in flattened:
                if isinstance(c, ASTAndNode):
                    and_terms = {repr(tc) for tc in c.children}
                    flattened_terms = {repr(fc) for fc in flattened if fc is not c}
                    if and_terms & flattened_terms:
                        # Only skip if other terms exist
                        if len(flattened) > 1:
                            continue
                result_children.append(c)

            if not result_children:
                return ASTFalseNode()
            if len(result_children) == 1:
                return result_children[0]

            return ASTOrNode(result_children)

        def visit_ASTNotNode(self, node: ASTNotNode) -> ASTNode:
            child = self.transform(node.child)
            # Double negation elimination
            if isinstance(child, ASTNotNode):
                return self.transform(child.child)
            return ASTNotNode(child)

        def visit_ASTTermNode(self, node: ASTTermNode) -> ASTNode:
            return node

        def visit_ASTTrueNode(self, node: "ASTTrueNode") -> ASTNode:
            return node

        def visit_ASTFalseNode(self, node: "ASTFalseNode") -> ASTNode:
            return node

# TODO: review/retouch (applies to all transformations really)

class RobustSimplifier(Transformer):
    """
    Safely simplifies an AST, handling edge cases:
    - Flatten AND/OR nodes
    - Remove duplicates
    - Fold constants
    - Handle absorption carefully
    - Replace empty AND/OR with TRUE/FALSE
    """

    def visit_ASTAndNode(self, node: ASTAndNode) -> ASTNode:
        children = [self.transform(c) for c in node.children]

        # Flatten nested ANDs and remove duplicates
        flattened = []
        seen = set()
        for c in children:
            if isinstance(c, ASTAndNode):
                for gc in c.children:
                    key = repr(gc)
                    if key not in seen:
                        seen.add(key)
                        flattened.append(gc)
            else:
                key = repr(c)
                if key not in seen:
                    seen.add(key)
                    flattened.append(c)

        # Constant folding
        if any(isinstance(c, ASTFalseNode) for c in flattened):
            return ASTFalseNode()
        flattened = [c for c in flattened if not isinstance(c, ASTTrueNode)]
        if not flattened:
            return ASTTrueNode()
        if len(flattened) == 1:
            return flattened[0]

        # Absorption: remove OR children that are redundant
        result_children = []
        for c in flattened:
            if isinstance(c, ASTOrNode):
                or_terms = {repr(tc) for tc in c.children}
                flattened_terms = {repr(fc) for fc in flattened if fc is not c}
                if or_terms & flattened_terms:
                    # Only skip if other terms exist, never remove last child
                    if len(flattened) > 1:
                        continue
            result_children.append(c)

        if not result_children:
            return ASTTrueNode()
        if len(result_children) == 1:
            return result_children[0]

        return ASTAndNode(result_children)

    def visit_ASTOrNode(self, node: ASTOrNode) -> ASTNode:
        children = [self.transform(c) for c in node.children]

        # Flatten nested ORs and remove duplicates
        flattened = []
        seen = set()
        for c in children:
            if isinstance(c, ASTOrNode):
                for gc in c.children:
                    key = repr(gc)
                    if key not in seen:
                        seen.add(key)
                        flattened.append(gc)
            else:
                key = repr(c)
                if key not in seen:
                    seen.add(key)
                    flattened.append(c)

        # Constant folding
        if any(isinstance(c, ASTTrueNode) for c in flattened):
            return ASTTrueNode()
        flattened = [c for c in flattened if not isinstance(c, ASTFalseNode)]
        if not flattened:
            return ASTFalseNode()
        if len(flattened) == 1:
            return flattened[0]

        # Absorption: remove AND children that are redundant
        result_children = []
        for c in flattened:
            if isinstance(c, ASTAndNode):
                and_terms = {repr(tc) for tc in c.children}
                flattened_terms = {repr(fc) for fc in flattened if fc is not c}
                if and_terms & flattened_terms:
                    # Only skip if other terms exist
                    if len(flattened) > 1:
                        continue
            result_children.append(c)

        if not result_children:
            return ASTFalseNode()
        if len(result_children) == 1:
            return result_children[0]

        return ASTOrNode(result_children)

    def visit_ASTNotNode(self, node: ASTNotNode) -> ASTNode:
        child = self.transform(node.child)
        # Double negation elimination
        if isinstance(child, ASTNotNode):
            return self.transform(child.child)
        return ASTNotNode(child)

    def visit_ASTTermNode(self, node: ASTTermNode) -> ASTNode:
        return node

    def visit_ASTTrueNode(self, node: "ASTTrueNode") -> ASTNode:
        return node

    def visit_ASTFalseNode(self, node: "ASTFalseNode") -> ASTNode:
        return node

# TODO: add a evaluation optimizing transformer
# which will reorder and terms in increasing order of postings list length
# inverted_index will need to cache posting list lengths, and expose a method to get them


class TransformationPipeline:
    def __init__(self, transformers: list[Transformer]):
        self.transformers = transformers

    def transform(self, node: ASTNode) -> ASTNode:
        for transformer in self.transformers:
            node = transformer.transform(node)
        return node
