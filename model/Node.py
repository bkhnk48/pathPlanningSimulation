from .TimeWindowEdge import TimeWindowEdge
from .Edge import HoldingEdge, MovingEdge
from .RestrictionEdge import RestrictionEdge
from .RestrictionNode import RestrictionNode
from .TimeWindowNode import TimeWindowNode

class Node:
    def __init__(self, ID):
        self.ID = ID

    def __repr__(self):
        return f"Node(id={self.id}, label='{self.label}')"
    
    def create_edge(self, node, M, d, e):
        if isinstance(node, Node) and not isinstance(node, (TimeWindowNode, RestrictionNode)):
            if node.ID % M == self.ID % M and ((node.ID - self.ID) // M == d):
                return HoldingEdge(self, node, d, d)
            elif node.ID % M != self.ID % M:
                return MovingEdge(self, node, e[4])

        if isinstance(node, RestrictionNode):
            return RestrictionEdge(self, node, e[4], "Restriction")
        
        if isinstance(node, TimeWindowNode):
            return TimeWindowEdge(self, node, e[4], "TimeWindows")
        
        return None  # This handles any unmatched conditions or types