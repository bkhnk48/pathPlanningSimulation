from .Event import Event
import pdb
class HaltingEvent(Event):
    def __init__(self, startTime, endTime, agv, graph, start_node, end_node):
        super().__init__(startTime, endTime, agv, graph)
        self.start_node = start_node
        self.end_node = end_node

    def updateGraph(self):
        if(self.endTime >= self.graph.H):
            pass
            #self.graph.update_edge(self.start_node, self.end_node, actual_time)  # Use self.graph instead of Graph
            #self.graph.handle_edge_modifications(self.start_node, self.end_node, self.agv)  # Use self.graph instead of Graph

    def calculateCost(self):
        # Tính chi phí dựa trên thời gian di chuyển thực tế
        cost_increase = self.endTime - self.startTime
        self.agv.cost += cost_increase  # Cập nhật chi phí của AGV
        return cost_increase

    def process(self):
        #pdb.set_trace()
        # Thực hiện cập nhật đồ thị khi xử lý sự kiện di chuyển
        #self.updateGraph()
        print(
            f"AGV {self.agv.id} moves from {self.start_node} to {self.end_node} but time outs!!!!"
        )
        self.calculateCost()
        print(f"The total cost of {self.agv.id} is {self.agv.cost}")
        #self.getNext()
