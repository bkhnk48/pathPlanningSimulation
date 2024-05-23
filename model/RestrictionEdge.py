from .Edge import Edge

class RestrictionEdge(Edge):
    def __init__(self, start_node, end_node, weight, label):
        super().__init__(start_node, end_node, weight)
        self.label = label

    def __repr__(self):
        return f"RestrictionEdge({self.start_node.id}, {self.end_node.id}, weight={self.weight}, restrictions={self.restrictions})"
