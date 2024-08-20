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
        self.agv = None

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
        
    def getEventForReaching(self, event):
        #next_vertex = event.agv.getNextNode().id
        #event.agv.path.add(self.id)
        #print(f"========={event.agv.path}")
        from .HoldingEvent import HoldingEvent
        from .ReachingTargetEvent import ReachingTargetEvent

        # Xác định kiểu sự kiện tiếp theo
        deltaT = (self.id // event.graph.numberOfNodesInSpaceGraph \
                                - (1 if self.id % event.graph.numberOfNodesInSpaceGraph == 0 else 0)) - (
            event.agv.current_node // event.graph.numberOfNodesInSpaceGraph \
                                - (1 if event.agv.current_node % event.graph.numberOfNodesInSpaceGraph == 0 else 0)
        )

        if (self.id % event.graph.numberOfNodesInSpaceGraph) == (
            event.agv.current_node % event.graph.numberOfNodesInSpaceGraph
        ):
            from .StartEvent import StartEvent
            if(not isinstance(event, StartEvent)):
                event.agv.move_to()
            return HoldingEvent(
                event.endTime,
                event.endTime + deltaT,
                event.agv,
                event.graph,
                deltaT,
            )
        elif self.id == event.agv.target_node.id:
            print(f"Target {event.agv.target_node.id}")
            #deltaT = getReal()
            return ReachingTargetEvent(
                event.endTime, event.endTime, event.agv, event.graph, self.id
            )
        else:
            print(f'{self.id}')
            if self.id == 30091:
                pdb.set_trace()
            return self.goToNextNode(event)

    # TODO Rename this here and in `getEventForReaching`
    def goToNextNode(self, event):
        from .Event import Event
        from .StartEvent import StartEvent
        from .MovingEvent import MovingEvent
        from .HaltingEvent import HaltingEvent
        if(not isinstance(event, StartEvent)):
            #pdb.set_trace()
            event.agv.move_to()
        #pdb.set_trace()
        next_vertex = event.agv.get_traces()[0].id
        deltaT= event.graph.getReal(event.agv.current_node, next_vertex)
        if event.endTime + deltaT < event.graph.graph_processor.H:
                #pdb.set_trace()
            return MovingEvent(
                event.endTime,
                event.endTime + deltaT,
                event.agv,
                event.graph,
                event.agv.current_node,
                next_vertex,
            )
        if(event.graph.graph_processor.printOut):
            print(f"H = {event.graph.graph_processor.H} and {event.endTime} + {deltaT}")
        return HaltingEvent(
            event.endTime,
            event.graph.graph_processor.H,
            event.agv,
            event.graph,
            event.agv.current_node,
            next_vertex,
        )
    
    def __repr__(self):
        return f"Node(id={self.id}, label='{self.label}', agv='{self.agv}')"   
