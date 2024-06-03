from .Edge import Edge

class TimeWindowEdge(Edge):
    def __init__(self, start_node, end_node, weight, label):
        super().__init__(start_node, end_node, 0, 1, weight)
        self.label = label

    def __repr__(self):
        return f"TimeWindowEdge({self.start_node}, {self.end_node}, weight={self.weight}, label={self.label})"
    
    def make_permanent(self):
        # This method could be used to convert a temporary edge into a permanent one
        self.temporary = False
        print(f"TimeWindowEdge from {self.start_node.id} to {self.end_node.id} made permanent.")
