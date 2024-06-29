from .Node import Node

class TimeWindowNode(Node):
    def __init__(self, ID, time_window):
        super().__init__(ID)
        self.time_window = time_window  # Time window in which the node can be accessed
        self.earliness = float('-inf')
        self.tardiness = float('inf')

    def set_time_window(self, earliness, tardiness):
        self.earliness = earliness
        self.tardiness = tardiness
        
    def create_edge(self, node, M, d, e):
        # Does nothing and returns None, effectively preventing the creation of any edge.
        return None
    
    def __repr__(self):
        return f"TimeWindowNode(ID={self.id}, time_window={self.time_window})"
