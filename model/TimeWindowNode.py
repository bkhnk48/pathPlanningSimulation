from .Node import Node
from .Edge import TimeWindowEdge

class TimeWindowNode(Node):
    def __init__(self, id, label=None, earliness=None, tardiness=None):
        super().__init__(id, label)
        self.earliness = earliness
        self.tardiness = tardiness

    def create_edge(self, node, M, d, e):
        if isinstance(node, TimeWindowNode):
            return TimeWindowEdge(self, node, e[4], "TimeWindows")
        else:
            return None
