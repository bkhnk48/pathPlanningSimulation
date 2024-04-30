from .Event import Event
class StartEvent(Event):
    def __init__(self, startTime, endTime, agv, graph):
        super().__init__(startTime, endTime, agv, graph)

    def process(self):
        print(f"StartEvent processed at time {self.startTime} for AGV {self.agv.id}. AGV is currently at node {self.agv.current_node}.")
        #self.determine_next_event()
        self.getNext()
