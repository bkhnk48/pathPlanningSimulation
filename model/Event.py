from .utility import utility
from .Graph import Graph
import subprocess
from discrevpy import simulator
from .AGV import AGV
from .Edge import Edge
import pdb;
import os
from collections import defaultdict

numberOfNodesInSpaceGraph = 0
debug = 0
allAGVs = {}

class Event:
    def __init__(self, startTime, endTime, agv, graph):
        self.startTime = int(startTime)
        self.endTime = int(endTime)
        self.agv = agv
        self.graph = graph
        self.pns_path = ''

    def setValue(name, value):
        if(name == "debug"):
            global debug
            debug = value
        if(name == "numberOfNodesInSpaceGraph"):
            global numberOfNodesInSpaceGraph
            numberOfNodesInSpaceGraph = value
        if(name == "allAGVs"):
            global allAGVs
            allAGVs = value
    
    def getValue(name):
        if(name == "debug"):
            global debug
            return debug
        if(name == "numberOfNodesInSpaceGraph"):
            global numberOfNodesInSpaceGraph
            return numberOfNodesInSpaceGraph
        if(name == "allAGVs"):
            global allAGVs
            return allAGVs
    

    def process(self):
        edge = self.graph.get_edge(self.start_node, self.end_node)
        if edge is not None:
            print(f"Edge found from {self.start_node} to {self.end_node} with weight {edge}")
        else:
            print(f"No edge found from {self.start_node} to {self.end_node}")
    def __repr__(self):
        return f"{self.type}(time={self.time}, agv_id={self.agv.id})"

    def getWait(self, waittime):
        obj = utility()
        graph = Graph(self.x)
        self.pos = self.pos + waittime * obj.M
        self.time = self.time + waittime
        graph.writefile(self.pos, 1)

    def getReal(self, currentpos, nextpos, realtime):
        obj = utility()
        graph = Graph(self.x)
        nextpos = obj.M * (
            int(self.pos / obj.M) + obj.matrix[currentpos, nextpos]
        ) + obj.getid(nextpos)
        graph.update(self.pos, nextpos, realtime)
        self.x = graph.matrix
        self.time = self.time + realtime
        self.pos = obj.M * (int(self.pos / obj.M) + realtime) + obj.getid(nextpos)
        graph.writefile(self.pos, 1)

    def getForecast(self, nextpos, forecastime):
        obj = utility()
        self.pos = obj.M * (int(self.pos / obj.M) + forecastime) + obj.getid(nextpos)
        self.time = self.time + forecastime
        graph = Graph(self.x)
        graph.writefile(self.pos, 1)

    def getNext(self):
        if self.graph.version == self.agv.versionOfGraph and self.graph.version != -1:
            # Nếu đồ thị hiện tại đã được dùng để tìm đường cho AGV
            next_vertex = self.agv.getNextNode()  # Giả định phương thức này tồn tại
        else:
            # Nếu đồ thị phiên bản này chưa dùng để tìm đường cho AGV, thì cần tìm lại đường đi
            self.updateGraph()
            filename = self.saveGraph()
            if (len(self.pns_path) == 0):
                self.pns_path = input('Nhập vào đường dẫn của pns-seq: ')
            lenh = f"{self.pns_path}/pns-seq -f {filename} > seq-f.txt"
            subprocess.run(lenh, shell=True)
            lenh = "python3 filter.py > traces.txt"
            subprocess.run(lenh, shell=True)
            self.setTracesForAllAGVs()
            next_vertex = self.agv.getNextNode()

        # Xác định kiểu sự kiện tiếp theo
        global numberOfNodesInSpaceGraph
        deltaT = (next_vertex / numberOfNodesInSpaceGraph) - (self.agv.current_node / numberOfNodesInSpaceGraph)
        if (next_vertex % numberOfNodesInSpaceGraph) == (self.agv.current_node % numberOfNodesInSpaceGraph):
            new_event = HoldingEvent(self.endTime, self.endTime + deltaT, self.agv, graph, deltaT)
        elif next_vertex is self.agv.target_node:
            new_event = ReachingTarget(self.endTime, self.endTime, self.agv, graph, next_vertex)
        else:
            new_event = MovingEvent(
                self.endTime, self.endTime + deltaT, self.agv, graph, self.agv.current_node, next_vertex
            )

        # Lên lịch cho sự kiện mới
        #new_event.setValue("allAGVs", self.allAGVs)
        simulator.schedule(new_event.endTime, new_event.getNext, graph)

    def updateGraph(self):
        pass
        # Assuming that `self.graph` is an instance of `Graph`
        #edge = self.graph.get_edge(self.agv.start_node, self.end_node)
        #if edge:
            # Proceed with your logic
            #print("Edge found:", edge)
        #else:
            #print("No edge found between", self.start_node, "and", self.end_node)

    def saveGraph(self):
        # Lưu đồ thị vào file DIMACS và trả về tên file
        filename = "current_graph.dimacs"
        # Code để lưu đồ thị vào file
        return filename

    def calculateCost(self):
        # Increase cost by the actual time spent in holding
        cost_increase = self.endTime - self.startTime
        self.agv.cost += cost_increase
        return cost_increase

    def run_pns_sequence(self, filename):
        command = f"./pns-seq -f {filename} > seq-f.txt"
        subprocess.run(command, shell=True)
        command = "python3 filter.py > traces.txt"
        subprocess.run(command, shell=True)

    def setTracesForAllAGVs(self):
        # Đọc và xử lý file traces để lấy các đỉnh tiếp theo
        #with open(filename, "r") as file:
        #    traces = file.read().split()
        #return traces
        if not self.graph.map:
            self.graph.setTrace('traces.txt')
        self.agv.traces = self.graph.getTrace(self.agv.id)
        global allAGVs
        for a in allAGVs:
            if(a.id != self.agv.id):
                if(a.versionOfGraph < self.graph.version):
            	    a.traces = self.graph.getTrace(a.id)
            	    a.versionOfGraph = self.graph.version


def get_largest_id_from_map(filename):
    largest_id = 0
    with open(filename, "r") as file:
        for line in file:
            parts = line.strip().split()
            if parts[0] == "a":  # Assuming arcs start with 'a'
                # Parse the node IDs from the arc definition
                id1, id2 = int(parts[1]), int(parts[2])
                largest_id = max(largest_id, id1, id2)
    return largest_id


class HoldingEvent(Event):
    def __init__(self, startTime, endTime, agv, graph, duration):
        super().__init__(startTime, endTime, agv, graph)
        self.duration = duration
        self.largest_id = get_largest_id_from_map("map.txt")

    def updateGraph(self):
        # Calculate the next node based on the current node, duration, and largest ID
        current_node = self.agv.current_node
        next_node = current_node + (self.duration * self.largest_id) + 1

        # Check if this node exists in the graph and update accordingly
        if next_node in self.graph.nodes:
            self.graph.update_node(current_node, next_node)
        else:
            print("Calculated next node does not exist in the graph.")

        # Update the AGV's current node to the new node
        self.agv.current_node = next_node

    def process(self):
        added_cost = self.calculateCost()
        print(
            f"Processed HoldingEvent for AGV {self.agv.id}, added cost: {added_cost}, moving to node {self.agv.current_node}"
        )
        self.updateGraph()


class MovingEvent(Event):
    def __init__(self, startTime, endTime, agv, graph, start_node, end_node):
        super().__init__(startTime, endTime, agv, graph)
        self.start_node = start_node
        self.end_node = end_node

    def updateGraph(self):
        actual_time = self.endTime - self.startTime
        edge = self.graph.get_edge(self.start_node, self.end_node)  # Use self.graph instead of Graph
        predicted_time = edge.weight if edge else None

        if actual_time != predicted_time:
            self.graph.update_edge(self.start_node, self.end_node, actual_time, self.agv)  # Use self.graph instead of Graph
            self.graph.handle_edge_modifications(self.start_node, self.end_node, self.agv)  # Use self.graph instead of Graph

    def calculateCost(self):
        # Tính chi phí dựa trên thời gian di chuyển thực tế
        cost_increase = self.endTime - self.startTime
        AGV.cost += cost_increase  # Cập nhật chi phí của AGV
        return cost_increase

    def process(self):
        # Thực hiện cập nhật đồ thị khi xử lý sự kiện di chuyển
        self.updateGraph()
        print(
            f"AGV {self.agv.id} moves from {self.start_node} to {self.end_node} taking actual time {self.endTime - self.startTime}"
        )

class ReachingTarget(Event):
    def __init__(self, startTime, endTime, agv, graph, target_node):
        super().__init__(startTime, endTime, agv, graph)
        self.target_node = target_node

    def updateGraph(self):
        # Không làm gì cả, vì đây là sự kiện đạt đến mục tiêu
        pass

    def calculateCost(self):
        # Retrieve the weight of the last edge traversed by the AGV
        if AGV.previous_node is not None and self.target_node is not None:
            last_edge_weight = Graph.get_edge(AGV.previous_node, self.target_node)
            if last_edge_weight is not None:
                # Calculate cost based on the weight of the last edge
                cost_increase = last_edge_weight
                AGV.update_cost(cost_increase)
                print(
                    f"Cost for reaching target node {self.target_node} is based on last edge weight: {cost_increase}."
                )
            else:
                print("No last edge found; no cost added.")
        else:
            print("Previous node or target node not set; no cost calculated.")

    def process(self):
        # Đây là phương thức để xử lý khi AGV đạt đến mục tiêu
        print(
            f"AGV {AGV.id} has reached the target node {self.target_node} at time {self.endTime}"
        )
        self.calculateCost()  # Calculate and update the cost of reaching the target
        self.updateGraph(self.graph)  # Optional: update the graph if necessary


class TimeWindowsEvent(Event):
    def __init__(self, startTime, endTime, agv, graph, target_node):
        super().__init__(startTime, endTime, agv, graph)
        self.target_node = target_node  # Mục tiêu mà AGV phải đạt đến trong một khoảng thời gian nhất định

    def calculateCost(self):
        # Chi phí dựa trên trọng số của cung mà AGV đi trên đồ thị TSG
        edge = self.graph.get_edge(self.agv.current_node, self.target_node)
        if edge:
            cost_increase = edge.weight
            AGV.cost += cost_increase  # Cập nhật chi phí của AGV
            print(
                f"Cost increased by {cost_increase} for AGV {AGV.id} due to TimeWindowsEvent at {self.target_node}"
            )
        else:
            print("No edge found or incorrect edge weight.")

    def getNext(self):
        # Tính toán chi phí
        self.calculateCost()
        # Có thể thực hiện các hành động tiếp theo tùy thuộc vào logic của bạn
        # Ví dụ: kiểm tra xem có sự kiện tiếp theo cần được lên lịch không

    def process(self):
        # Xử lý khi sự kiện được gọi
        print(
            f"AGV {self.agv.id} processes TimeWindowsEvent at {self.target_node} at time {self.endTime}"
        )
        self.getNext(self.graph)


class RestrictionEvent(Event):
    def __init__(self, startTime, endTime, agv, graph, start_node, end_node):
        super().__init__(startTime, endTime, agv, graph)
        self.start_node = start_node
        self.end_node = end_node

    def updateGraph(self):
        # Giả định thời gian di chuyển thực tế khác với dự đoán do các ràng buộc đặc biệt
        actual_time = self.endTime - self.startTime
        predicted_time = Graph.get_edge(self.start_node, self.end_node).weight

        if actual_time != predicted_time:
            # Cập nhật trọng số của cung trên đồ thị để phản ánh thời gian thực tế
            Graph.update_edge(self.start_node, self.end_node, actual_time)

            # Đánh dấu AGV cuối cùng thay đổi đồ thị
            Graph.lastChangedByAGV = AGV.id

    def calculateCost(self):
        # Chi phí của AGV sẽ được tăng thêm một lượng bằng trọng số của cung mà AGV đi trên đồ thị TSG
        edge = Graph.get_edge(self.start_node, self.end_node)
        if edge:
            cost_increase = edge.weight
            AGV.cost += cost_increase
            print(
                f"Cost increased by {cost_increase} for AGV {AGV.id} due to RestrictionEvent from {self.start_node} to {self.end_node}"
            )
        else:
            print("No edge found or incorrect edge weight.")

    def process(self):
        # Xử lý khi sự kiện được gọi
        print(
            f"AGV {AGV.id} moves from {self.start_node} to {self.end_node} under restrictions, taking {self.endTime - self.startTime} seconds"
        )
        self.updateGraph(self.graph)
        self.calculateCost()


class StartEvent(Event):
    def __init__(self, startTime, endTime, agv, graph):
        super().__init__(startTime, endTime, agv, graph)

    def process(self):
        print(f"StartEvent processed at time {self.startTime} for AGV {self.agv.id}. AGV is currently at node {self.agv.current_node}.")
        #self.determine_next_event()
        self.getNext()

    def determine_next_event(self):
        # Example logic to determine the next event type
        if(debug == 1):
            pdb.set_trace()
        if self.graph.has_initial_movement(self.agv.current_node):
            next_node = (
                self.agv.current_node + 1
            )  # Assuming the next node is simply the next sequential node
            next_event = MovingEvent(
                startTime=self.endTime,
                endTime=self.endTime + 15,  # Assuming movement takes an additional 10 units of time
                agv=self.agv,
                graph=self.graph,
                start_node=self.agv.current_node,
                end_node=next_node,
            )
        else:
            next_event = HoldingEvent(
                startTime=self.endTime,
                endTime=self.endTime + 10,  # Assuming holding also takes 10 units of time
                agv=self.agv,
                graph=self.graph,
                duration=10,
            )

        simulator.schedule(next_event.startTime, next_event.process)
