#from .TimeWindowEdge import TimeWindowEdge
#from .Edge import HoldingEdge, MovingEdge
#from .RestrictionEdge import RestrictionEdge
#from .RestrictionNode import RestrictionNode
#from .TimeWindowNode import TimeWindowNode
import pdb

class Node:
    def __init__(self, id,label=None):
        if not isinstance(id, int):
            raise ValueError(f"Tham số {id} truyền vào phải là số nguyên")
        self.id = id
        self.label=label
        self.edges = []

    def create_edge(self, node, M, d, e, debug = False):
        if(debug):
            pdb.set_trace()
        from .RestrictionNode import RestrictionNode
        from .TimeWindowNode import TimeWindowNode
        from .Edge import HoldingEdge
        from .RestrictionEdge import RestrictionEdge
        from .TimeWindowEdge import TimeWindowEdge 
        from .Edge import MovingEdge
        if node.id % M == self.id % M and \
        ((node.id - self.id) // M == d) and \
        isinstance(node, Node) and \
        not isinstance(node, RestrictionNode) and \
        not isinstance(node, TimeWindowNode):
            return HoldingEdge(self, node, e[2], e[3], d, d)
        elif isinstance(node, RestrictionNode):
            return RestrictionEdge(self, node, e, "Restriction")
        elif isinstance(node, TimeWindowNode):
            return TimeWindowEdge(self, node, e[4], "TimeWindows")
        elif isinstance(node, Node):
            if node.id % M != self.id % M:
                return MovingEdge(self, node, e[2], e[3], e[4])
        else:
            return None
        
    def connect(self, other_node, weight, graph):
        graph.add_edge(self.id, other_node.id, weight)
    
    def __repr__(self):
        return f"Node(id={self.id}, label='{self.label}')"   
