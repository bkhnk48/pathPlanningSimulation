from .Node import Node
from RestrictionEdge import RestrictionEdge

class RestrictionNode(Node):
    def __init__(self, ID, restrictions):
        super().__init__(ID)
        self.restrictions = restrictions  # Restrictions associated with the node
        
    def create_edge(self, node, M, d, e):
        # Always returns a RestrictionEdge regardless of other node types or conditions.
        return RestrictionEdge(self, node, e[4], "Restriction")

    def __repr__(self):
        return f"RestrictionNode(ID={self.ID}, restrictions={self.restrictions})"
