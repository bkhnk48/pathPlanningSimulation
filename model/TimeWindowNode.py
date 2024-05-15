from .Node import Node
class TimeWindowNode(Node):
    def __init__(self, id, label=None):
        super().__init__(id,label)

    def create_edge(self, node, M, d, e):
        if isinstance(node, TimeWindowNode):
            return TimeWindowEdge(self, node, e[4], "TimeWindows")
        else:
            return None
