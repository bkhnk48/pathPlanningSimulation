from .utility import utility
from .Graph import Graph
import subprocess
from discrevpy import simulator
from .AGV import AGV
from .Edge import Edge
import pdb
import os
from collections import defaultdict
import config

numberOfNodesInSpaceGraph = 0
debug = 0
allAGVs = {}


class Event:
    def __init__(self, startTime, endTime, agv, graph):
        self.startTime = int(startTime)
        self.endTime = int(endTime)
        self.agv = agv
        self.graph = graph
        self.pns_path = ""

    def setValue(name, value):
        if name == "debug":
            global debug
            debug = value
        if name == "numberOfNodesInSpaceGraph":
            global numberOfNodesInSpaceGraph
            numberOfNodesInSpaceGraph = value
        if name == "allAGVs":
            global allAGVs
            allAGVs = value

    def getValue(name):
        if name == "debug":
            global debug
            return debug
        if name == "numberOfNodesInSpaceGraph":
            global numberOfNodesInSpaceGraph
            return numberOfNodesInSpaceGraph
        if name == "allAGVs":
            global allAGVs
            return allAGVs

    def process(self):
        #pdb.set_trace()
        edge = self.graph.get_edge(self.start_node, self.end_node)
        if edge is not None:
            print(
                f"Edge found from {self.start_node} to {self.end_node} with weight {edge}"
            )
        else:
            print(f"No edge found from {self.start_node} to {self.end_node}")

    def __repr__(self):
        return f"(time=[{self.startTime}, {self.endTime}], agv_id={self.agv.id})"

    def getWait(self, wait_time):
        obj = utility()
        graph = Graph(self.x)
        self.pos = self.pos + wait_time * obj.M
        self.time = self.time + wait_time
        graph.writefile(self.pos, 1)

    """def getReal(self, currentpos, nextpos, realtime):
        obj = utility()
        graph = Graph(self.x)
        nextpos = obj.M * (
            int(self.pos / obj.M) + obj.matrix[currentpos, nextpos]
        ) + obj.getid(nextpos)
        graph.update(self.pos, nextpos, realtime)
        self.x = graph.matrix
        self.time = self.time + realtime
        self.pos = obj.M * (int(self.pos / obj.M) + realtime) + obj.getid(nextpos)
        graph.writefile(self.pos, 1)"""

    def getForecast(self, nextpos, forecastime):
        obj = utility()
        self.pos = obj.M * (int(self.pos / obj.M) + forecastime) + obj.getid(nextpos)
        self.time = self.time + forecastime
        graph = Graph(self.x)
        graph.writefile(self.pos, 1)

    def saveGraph(self):
        # Lưu đồ thị vào file DIMACS và trả về tên file
        filename = "TSG.txt"
        #filename = "input_dimacs/supply_03_demand_69_edit.txt"
        # Code để lưu đồ thị vào file
        return filename

    def getNext(self):
        from .HoldingEvent import HoldingEvent
        from .MovingEvent import MovingEvent
        from .HaltingEvent import HaltingEvent
        from model.forecasting_model_module.ForecastingModel import ForecastingModel, DimacsFileReader
        #pdb.set_trace()
        if self.graph.numberOfNodesInSpaceGraph == -1:
            global numberOfNodesInSpaceGraph
            self.graph.numberOfNodesInSpaceGraph = numberOfNodesInSpaceGraph

        if (
            self.graph.version != self.agv.versionOfGraph
            or self.graph.version == -1
        ):
            self.find_path(DimacsFileReader, ForecastingModel)
        #pdb.set_trace()
        next_vertex = self.agv.getNextNode()
        new_event = next_vertex.getEventForReaching(self)
        # Lên lịch cho sự kiện mới
        # new_event.setValue("allAGVs", self.allAGVs)
        # simulator.schedule(new_event.endTime, new_event.getNext, self.graph)
        #simulator.schedule(new_event.endTime, new_event.process)
        return new_event


    # TODO Rename this here and in `getNext`
    def find_path(self, DimacsFileReader, ForecastingModel):
        if self.graph.version == -1 == self.agv.versionOfGraph:
            #pdb.set_trace()
            self.updateGraph()
        filename = self.saveGraph()

        if config.solver_choice == 'solver':
            self.createTracesFromSolver(DimacsFileReader, filename, ForecastingModel)
                    #self.graph.version += 1
        elif len(self.pns_path) == 0:
            self.pns_path = input("Enter the path for pns-seq: ")
            command = f"{self.pns_path}/pns-seq -f {filename} > seq-f.txt"
            print("Running network-simplex:", command)
            subprocess.run(command, shell=True)

        if config.solver_choice != 'solver':
            command = "python3 filter.py > traces.txt"
            subprocess.run(command, shell=True)

        #pdb.set_trace()
        print(f"{self} {self.startTime} {self.endTime}")
        if self.graph.version == -1 == self.agv.versionOfGraph:
            self.graph.version += 1
        self.setTracesForAllAGVs()

    # TODO Rename this here and in `getNext`
    def createTracesFromSolver(self, DimacsFileReader, filename, ForecastingModel):
        print("Running ForecastingModel...")
        # Assuming `filename` is a path to the file with necessary data for the model
        dimacs_file_reader = DimacsFileReader(filename)
        dimacs_file_reader.read_custom_dimacs()
        problem_info, supply_nodes_dict, demand_nodes_dict, zero_nodes_dict, arc_descriptors_dict, earliness_tardiness_dict = dimacs_file_reader.get_all_dicts()
        model = ForecastingModel(problem_info, supply_nodes_dict, demand_nodes_dict, zero_nodes_dict, arc_descriptors_dict, earliness_tardiness_dict)
        #if(model == None):
        #pdb.set_trace()
        model.solve()
        model.output_solution()
        model.save_solution(filename, "test_ouput") # Huy: sửa lại để log ra file
        model.create_traces("traces.txt", self.graph.version)

    def updateGraph(self):
        pass
        # Assuming that `self.graph` is an instance of `Graph`
        # edge = self.graph.get_edge(self.agv.start_node, self.end_node)
        # if edge:
        # Proceed with your logic
        # print("Edge found:", edge)
        # else:
        # print("No edge found between", self.start_node, "and", self.end_node)

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
        # with open(filename, "r") as file:
        #    traces = file.read().split()
        # return traces
        # if not self.graph.map:
        #     self.graph.setTrace("traces.txt")
        #pdb.set_trace()
        self.graph.setTrace("traces.txt")
        self.agv.traces = self.graph.getTrace(self.agv)
        self.agv.versionOfGraph = self.graph.version
        self.agv.target_node = self.agv.traces[len(self.agv.traces) - 1]
        global allAGVs
        for a in allAGVs:
            if a.id != self.agv.id and a.versionOfGraph < self.graph.version:
                a.traces = self.graph.getTrace(a)
                a.versionOfGraph = self.graph.version
                a.target_node = a.traces[len(a.traces) - 1]


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
