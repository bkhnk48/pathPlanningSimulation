class Edge:
    """ Represents a directed edge in a graph with a weight. """
    def __init__(self, start_node, end_node, weight):
        if start_node == end_node:
            raise ValueError("Start and end nodes cannot be the same")
        self.start_node = start_node
        self.end_node = end_node
        self.weight = weight
        
    def __repr__(self):
        return f"Edge({self.start_node}, {self.end_node}, weight={self.weight})"

class HoldingEdge(Edge):
    """ Represents an edge where an AGV must hold for a minimum time. """
    def __init__(self, start_node, end_node, weight, min_hold_time):
        super().__init__(start_node, end_node, weight)
        self.min_hold_time = min_hold_time

    def __repr__(self):
        return f"HoldingEdge({self.start_node}, {self.end_node}, weight={self.weight}, hold_time={self.min_hold_time})"

class MovingEdge(Edge):
    """ Represents an edge that might have dynamic conditions like speed limits. """
    def __init__(self, start_node, end_node, weight, speed_limit=None):
        super().__init__(start_node, end_node, weight)
        self.speed_limit = speed_limit

    def update_weight_due_to_traffic(self, new_weight):
        if new_weight != self.weight:
            self.weight = new_weight
            print(f"Weight updated for MovingEdge from {self.start_node} to {self.end_node} to {new_weight}")

class ArtificialEdge(Edge):
    """ Represents a temporary or conditional edge in the graph. """
    def __init__(self, start_node, end_node, weight, temporary=True):
        super().__init__(start_node, end_node, weight)
        self.temporary = temporary

    def make_permanent(self):
        if self.temporary:
            self.temporary = False
            print(f"ArtificialEdge from {self.start_node} to {self.end_node} made permanent")
        else:
            print("Edge is already permanent")

    def disable_temporarily(self):
        if not self.temporary:
            self.temporary = True
            print(f"ArtificialEdge from {self.start_node} to {self.end_node} temporarily disabled")