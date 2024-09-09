from .Event import Event
from discrevpy import simulator
import pdb
    
class StartEvent(Event):
    def __init__(self, startTime, endTime, agv, graph):
        super().__init__(startTime, endTime, agv, graph)
        print(self)

    def process(self):
        #pdb.set_trace()
        if(self.graph.graph_processor.printOut):
            print(f"StartEvent processed at time {self.startTime} for {self.agv.id}. The AGV is currently at node {self.agv.current_node}.")
        #self.determine_next_event()
        #self.getNext(True)
        self.getNext()
        
    def __str__(self):
        return f"StartEvent for {self.agv.id} to kick off its route from {self.agv.current_node} at {self.startTime}"
    
    def getNext(self, debug = False):
        self.solve()
        #next_vertex = self.agv.getNextNode()
        if(debug):
            pdb.set_trace()
        next_node = self.graph.nodes[self.agv.current_node]
        #new_event = next_node.getEventForReaching(self)
        new_event = next_node.goToNextNode(self)
        simulator.schedule(new_event.endTime, new_event.process)
