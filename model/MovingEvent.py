from .Event import Event
import inspect
import pdb
class MovingEvent(Event):
    def __init__(self, startTime, endTime, agv, graph, start_node, end_node):
        super().__init__(startTime, endTime, agv, graph)
        #pdb.set_trace()
        self.start_node = start_node
        self.end_node = end_node
        M = self.graph.numberOfNodesInSpaceGraph
        t1 = self.start_node // M - (self.graph.graph_processor.d if self.start_node % M == 0 else 0)
        if(t1 != self.startTime):
            if(self.graph.graph_processor.printOut):
                print("Errror")
            #pdb.set_trace()
            # Lấy thông tin về khung hiện tại
            """current_frame = inspect.currentframe()
            # Lấy tên của hàm gọi my_function
            caller_name = inspect.getframeinfo(current_frame.f_back).function
            if(self.graph.graph_processor.printOut):
                print(f'MovingEvent.py:19 {caller_name}')"""

    def updateGraph(self):
        actual_time = self.endTime - self.startTime
        #pdb.set_trace()
        #if(self.start_node == 10 or self.agv.id == 'AGV10'):
        #    pdb.set_trace()
        #weight_of_edge = self.graph.get_edge(self.start_node, self.end_node)  # Use self.graph instead of Graph
        M = self.graph.numberOfNodesInSpaceGraph
        t2 = self.end_node // M - (self.graph.graph_processor.d if self.end_node % M == 0 else 0)
        t1 = self.start_node // M - (self.graph.graph_processor.d if self.start_node % M == 0 else 0)
        #if(t1 != self.startTime):
        #    pdb.set_trace()
        real_end_node = self.endTime*M + (M if self.end_node % M == 0 else self.end_node % M)
        self.agv.path.add(real_end_node)
        
        if(real_end_node in self.graph.nodes):
            self.graph.nodes[real_end_node].agv = self.agv
        if self.start_node in self.graph.nodes:
            self.graph.nodes[self.start_node].agv = None
            """pdb.set_trace()
            self.graph.nodes[real_end_node].agv = self.graph.nodes[self.start_node].agv \
                if(self.graph.nodes[self.start_node].agv is not None) else self.graph.nodes[self.end_node].agv
        self.graph.nodes[self.start_node].agv = None"""
        
        weight_of_edge = t2 - t1
        predicted_time = weight_of_edge or None
        #if(real_end_node == 14987):
        #    pdb.set_trace()
        #pdb.set_trace()

        if actual_time != predicted_time:
            if self.end_node in self.graph.nodes:
                self.graph.nodes[self.end_node].agv = None
            print('=-==-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
            self.graph.update_graph(self.start_node, self.end_node, actual_time, self.agv.id)
            #pdb.set_trace()
            #self.agv.set_traces([self.graph.nodes[real_end_node]])
            self.agv.update_traces(self.end_node, self.graph.nodes[real_end_node])
            self.graph.nodes[real_end_node].agv = self.agv
            #self.graph.update_edge(self.start_node, self.end_node, actual_time)  # Use self.graph instead of Graph
            #self.graph.handle_edge_modifications(self.start_node, self.end_node, self.agv)  # Use self.graph instead of Graph

    def calculateCost(self):
        #pdb.set_trace()
        # Tính chi phí dựa trên thời gian di chuyển thực tế
        cost_increase = self.graph.graph_processor.alpha*(self.endTime - self.startTime)
        self.agv.cost += cost_increase  # Cập nhật chi phí của AGV
        return cost_increase

    def process(self):
        #if(self.endTime == 217):
        #    pdb.set_trace()
        self.calculateCost()
        # Thực hiện cập nhật đồ thị khi xử lý sự kiện di chuyển
        self.updateGraph()
        if(self.graph.graph_processor.printOut):
            print(
                f"AGV {self.agv.id} moves from {self.start_node} to {self.end_node} taking actual time {self.endTime - self.startTime}"
                )
        #pdb.set_trace()
        self.getNext()
