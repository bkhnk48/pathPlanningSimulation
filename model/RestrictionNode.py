from .Node import Node
class RestrictionNode(Node):
    def __init__(self, id, label=None):
        super().__init__(id,label)

    def create_edge(self, node, M, d, e):
        if isinstance(node, RestrictionNode):
            return RestrictionEdge(self, node, e[4], "Restriction")
        else:
            return None
