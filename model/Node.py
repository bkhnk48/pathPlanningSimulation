class Node:
    def __init__(self, id,label=None):
        self.id = id
        self.label=label
        self.edges = []

    def create_edge(self, node, M, d, e):
        if node.id % M == self.id % M and ((node.id - self.id) // M == d) and isinstance(node, Node) and not isinstance(node, RestrictionNode) and not isinstance(node, TimeWindowNode):
            return HoldingEdge(self, node, d, d)
        elif isinstance(node, RestrictionNode):
            return RestrictionEdge(self, node, e[4], "Restriction")
        elif isinstance(node, TimeWindowNode):
            return TimeWindowEdge(self, node, e[4], "TimeWindows")
        elif isinstance(node, Node):
            if node.id % M != self.id % M:
                return MovingEdge(self, node)
        else:
            return None
    
    def __repr__(self):
        return f"Node(id={self.id}, label='{self.label}')"   
