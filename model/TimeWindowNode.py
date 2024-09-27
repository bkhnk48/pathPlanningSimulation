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
        
    def calculate(self, reaching_time):
        if reaching_time >= self.earliness and reaching_time <= self.tardiness:
            return 0
        if reaching_time < self.earliness:
            return (-1)*(self.earliness - reaching_time)
        #if reaching_time > self.tardiness:
        return (reaching_time - self.tardiness)
        
    def create_edge(self, node, M, d, e):
        # Does nothing and returns None, effectively preventing the creation of any edge.
        return None
    
    def getEventForReaching(self, event):
        #next_vertex = event.agv.getNextNode().id
        from .ReachingTargetEvent import ReachingTargetEvent
        if self.id == event.agv.target_node.id:
            #pdb.set_trace()
            print(f"Target {event.agv.target_node.id}")
            #deltaT = getReal()
            return ReachingTargetEvent(
                event.endTime, event.endTime, event.agv, event.graph, self.id
            )
        return None
    
    def __repr__(self):
        return f"TimeWindowNode(ID={self.id}, time_window={self.time_window})"
