from model.utility import get_largest_id_from_map
import inspect
from sortedcontainers import SortedSet
import pdb
from inspect import currentframe, getframeinfo


class AGV:
    __allInstances = set()
    def __init__(self, id, current_node, graph, cost = 0, versionOfGraph = -1):
        self.id = id
        self.current_node = current_node
        self.previous_node = None
        self._target_node = None
        self.state = 'idle'
        self.cost = cost
        self.versionOfGraph = versionOfGraph
        self._traces = [] #các đỉnh sắp đi qua
        self.path = SortedSet([]) #các đỉnh đã đi qua 
        self.graph = graph
        self.graph.nodes[current_node].agv = self
        self.event = None
        AGV.__allInstances.add(self)
        
    @property
    def target_node(self):
        return self._target_node
    
    @staticmethod
    def allInstances():
        return AGV.__allInstances
    
    @target_node.setter
    def target_node(self, value):
        self._target_node = value
    def updateInfo(width, length, speed):
        self.width = width
        self.length = length
        self.speed = speed
        
    def update_cost(self, amount):
        self.cost += amount
        if(self.graph.graph_processor.printOut):
            print(f"Cost updated for AGV {self.id}: {self.cost}.")

    def getNextNode(self, endedEvent = False):
        #stack = inspect.stack()
        #for frame in stack[1:]:
        #pdb.set_trace()
            #print(f"Hàm '{frame.function}' được gọi từ file '{frame.filename}' tại dòng {frame.lineno}")
        if self._traces:
            if(endedEvent):
                #pdb.set_trace()
                self.current_node = self._traces.pop(0)
                """if (self._traces[0].id == 13899):
                    print("+++++++++++++++++++++++")"""
            if isinstance(self.current_node, int):
                self.path.add(self.current_node)
            else:
                self.path.add(self.current_node.id)
                self.current_node = self.current_node.id
            #print(f"{self.path}")
            
            next_node = self._traces[0]
            if(self.graph.graph_processor.printOut or True):
                print(f"AGV {self.id} is moving to next node: {next_node} from current node: {self.current_node}.")
            return next_node
        else:
            print(f"AGV {self.id} has no more nodes in the trace. Remaining at node: {self.current_node}.")
            return None
    
    def get_traces(self):
        """if(self._traces != None):
            if len(self._traces) >= 1:
                if self._traces[0].id == 13899:
                    #pdb.set_trace()
                    # Lấy thông tin về khung hiện tại
                    current_frame = inspect.currentframe()
                    # Lấy tên của hàm gọi my_function
                    caller_name = inspect.getframeinfo(current_frame.f_back).function
                    #if(self.graph.graph_processor.printOut):
                    print(f'AGV.py:74 {caller_name}')
                    print(f'{getframeinfo(currentframe()).filename.split("/")[-1]}:{getframeinfo(currentframe()).lineno} {self.id}', end=' ')"""
        return self._traces
    
    def set_traces(self, traces):
        """if(self._traces != None):
            if len(self._traces) >= 1:
                if self._traces[0].id == 13899:
                    #pdb.set_trace()
                    # Lấy thông tin về khung hiện tại
                    current_frame = inspect.currentframe()
                    # Lấy tên của hàm gọi my_function
                    caller_name = inspect.getframeinfo(current_frame.f_back).function
                    #if(self.graph.graph_processor.printOut):
                    print(f'AGV.py:88 {caller_name}')"""
        self._traces = traces
    
    def update_traces(self, predicted_id_node, real_node):
        #pdb.set_trace()
        index = 0
        for node in self._traces:
            if node.id == predicted_id_node:
                break
            else:
                index = index + 1
        self._traces[index] = real_node
    def move_to(self):
        if len(self._traces) >= 1:
            self.previous_node = self.current_node
            self.current_node = self.get_traces()[0].id
            self._traces.pop(0)
            self.state = 'moving'
            if(self.graph.graph_processor.printOut):
                print(f"AGV {self.id} moved from {self.previous_node} to {self.current_node}. State updated to 'idle'.")
            self.state = 'idle'
        else:
            if(self.graph.graph_processor.printOut):
                print(f"AGV {self.id} has no further destinations to move to.")

    def wait(self, duration):
        print(f"AGV {self.id} is waiting at node {self.current_node} for {duration} seconds.")
        self.state = 'waiting'
        # Simulate waiting
        self.state = 'idle'
        print(f"AGV {self.id} finished waiting at node {self.current_node}.")
    def add_traces(self, node):
        pdb.set_trace()
        self._traces.append(node)
        print(f"Node {node} added to AGV {self.id}'s trace. Current trace path: {self.traces}")

    def print_status(self):
        """ Utility method to print current status of the AGV """
        print(f"AGV {self.id}: Current Node: {self.current_node}, Previous Node: {self.previous_node}, State: {self.state}, Cost: {self.cost}, Upcoming Path: {self.traces}")
        
