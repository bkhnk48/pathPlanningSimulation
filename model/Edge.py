class Edge:
    def __init__(self, start_node, end_node, lower, upper, weight):
        self.start_node = start_node
        self.end_node = end_node
        self.weight = weight
        self.lower = lower
        self.upper = upper
        
    def __repr__(self):
        return f"Edge({self.start_node}, {self.end_node}, weight={self.weight})"
class HoldingEdge(Edge):
    def __init__(self, start_node, end_node, lower, upper, weight, min_hold_time):
        super().__init__(start_node, end_node, lower, upper, weight)
        self.min_hold_time = min_hold_time  # Minimum time an AGV has to hold on this edge

    def __repr__(self):
        return f"HoldingEdge({self.start_node}, {self.end_node}, weight={self.weight}, hold_time={self.min_hold_time})"

class MovingEdge(Edge):
    def __init__(self, start_node, end_node, lower, upper, weight, speed_limit=None):
        super().__init__(start_node, end_node, lower, upper, weight)
        self.speed_limit = speed_limit  # Optional attribute for speed limits

    def update_weight_due_to_traffic(self, new_weight):
        # This method could be used to dynamically adjust the weight of the edge based on traffic conditions
        self.weight = new_weight
        print(f"Weight of MovingEdge from {self.start_node.id} to {self.end_node.id} updated to {new_weight}")

class ArtificialEdge(Edge):
    def __init__(self, start_node, end_node, lower, upper, weight, temporary=False):
        super().__init__(start_node, end_node, lower, upper, weight)
        self.temporary = temporary  # Indicates if the edge is temporary

    def make_permanent(self):
        # This method could be used to convert a temporary edge into a permanent one
        self.temporary = False
        print(f"ArtificialEdge from {self.start_node.id} to {self.end_node.id} made permanent.")
