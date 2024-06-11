from .Event import Event
class StartEvent(Event):
    def __init__(self, startTime, endTime, agv, graph):
        super().__init__(startTime, endTime, agv, graph)

    def process(self):
        print(f"StartEvent processed at time {self.startTime} for {self.agv.id}. The AGV is currently at node {self.agv.current_node}.")
        #self.determine_next_event()
        self.getNext()
