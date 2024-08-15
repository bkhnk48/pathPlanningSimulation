from .Event import Event
import pdb
class MovingEvent(Event):
    def __init__(self, startTime, endTime, agv, graph, start_node, end_node):
        super().__init__(startTime, endTime, agv, graph)
        #pdb.set_trace()
        self.start_node = start_node
        self.end_node = end_node

    def updateGraph(self):
        actual_time = self.endTime - self.startTime
        pdb.set_trace()
        #if(self.start_node == 10 or self.agv.id == 'AGV10'):
        #    pdb.set_trace()
        #weight_of_edge = self.graph.get_edge(self.start_node, self.end_node)  # Use self.graph instead of Graph
        M = self.graph.numberOfNodesInSpaceGraph
        t2 = self.end_node // M - (1 if self.end_node % M == 0 else 0)
        t1 = self.start_node // M - (1 if self.start_node % M == 0 else 0)
        real_end_node = actual_time*M + (M if self.end_node % M == 0 else self.end_node % M)
        self.agv.path.add(real_end_node)
        
        if(real_end_node in self.graph.nodes):
            self.graph.nodes[real_end_node].agv = self.graph.nodes[self.start_node].agv \
                if(self.graph.nodes[self.start_node].agv is not None) else self.graph.nodes[self.end_node].agv
        self.graph.nodes[self.start_node].agv = None
        
        weight_of_edge = t2 - t1
        predicted_time = weight_of_edge or None
        #pdb.set_trace()

        if actual_time != predicted_time:
            self.graph.nodes[self.end_node].agv = None
            self.graph.update_graph(self.start_node, self.end_node, actual_time, self.agv.id)
            self.agv.traces = [self.graph.nodes[real_end_node]]
            #self.graph.update_edge(self.start_node, self.end_node, actual_time)  # Use self.graph instead of Graph
            #self.graph.handle_edge_modifications(self.start_node, self.end_node, self.agv)  # Use self.graph instead of Graph

    def calculateCost(self):
        #pdb.set_trace()
        # Tính chi phí dựa trên thời gian di chuyển thực tế
        cost_increase = self.graph.graph_processor.alpha*(self.endTime - self.startTime)
        self.agv.cost += cost_increase  # Cập nhật chi phí của AGV
        return cost_increase

    def process(self):
        #pdb.set_trace()
        self.calculateCost()
        # Thực hiện cập nhật đồ thị khi xử lý sự kiện di chuyển
        self.updateGraph()
        if(self.graph.graph_processor.printOut):
            print(
                f"AGV {self.agv.id} moves from {self.start_node} to {self.end_node} taking actual time {self.endTime - self.startTime}"
                )
        #pdb.set_trace()
        self.getNext()
