import networkx as nx
import pdb
import config
from collections import defaultdict

class NetworkXSolution:
    def __init__(self):#, edges_with_costs, started_nodes, target_nodes):
        self.started_nodes = None #started_nodes
        self.target_nodes = None #target_nodes
        self.edges_with_costs = None #edges_with_costs
        self.flowCost = 0
        self.flowDict = defaultdict(list)
        self.M = 0
    
    def read_dimac_file(self, file_path):
        G = nx.DiGraph()
        #pdb.set_trace()
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.split()
                if parts[0] == 'n':
                    ID = parts[1]
                    demand = (-1)*int(parts[2])
                    G.add_node(ID, demand = demand)
                elif parts[0] == 'a':
                    ID1 = (parts[1])
                    ID2 = (parts[2])
                    U = int(parts[4])
                    C = int(parts[5])
                    G.add_edge(ID1, ID2, weight=C, capacity=U)
        self.flowCost, self.flowDict = nx.network_simplex(G)
        config.totalSolving += 1
        #print(type(self.flowDict))
        #return [flowCost, flowDict]
        """print("flowCost:", flowCost)
        print("flowDict:", flowDict)"""
    def write_trace(self, file_path = 'traces.txt'):
        #pdb.set_trace()
        filtered_data = {}
        for key, sub_dict in self.flowDict.items():
            # Lọc các phần tử có giá trị khác 0
            filtered_sub_dict = {k: v for k, v in sub_dict.items() if v != 0}
            if filtered_sub_dict:
                filtered_data[key] = filtered_sub_dict
        self.flowDict = filtered_data

        with open(file_path, "w") as file:
            for key, value in self.flowDict.items():
                for inner_key, inner_value in value.items():
                    if(inner_value > 0):
                        s = int(key) // self.M + (self.M if int(key) // self.M == 0 else 0)
                        t = int(inner_key) // self.M + (self.M if int(inner_key) // self.M == 0 else 0)
                        cost = self.edges_with_costs.get((s, t), [-1, -1])[1]
                        result = inner_value*cost
                        #print(f"a {key} {inner_key} 0 + {result} = {result}")
                        file.write(f"a {key} {inner_key} 0 + {result} = {result}\n")

# Đường dẫn đến file DIMAC của bạn
"""file_path = input("Path to DIMAC file:")
read_dimac_file(file_path)"""
"""G = nx.DiGraph()
G.add_node("a", demand=-1)
G.add_node("c", demand=1)
G.add_edge("a", "b", weight=3, capacity=1)
G.add_edge("b", "c", weight=0, capacity=1)
G.add_edge("a", "c", weight=5, capacity=1)
flowCost, flowDict = nx.network_simplex(G)
print("flowCost:", flowCost)
print("flowDict:", flowDict)"""
