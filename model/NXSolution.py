import networkx as nx
import pdb

class NetworkXSolution:
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
        flowCost, flowDict = nx.network_simplex(G)
        return [flowCost, flowDict]
        """print("flowCost:", flowCost)
        print("flowDict:", flowDict)"""

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
