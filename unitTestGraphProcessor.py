from model.Graph import Graph#, graph
from model.AGV import AGV
from model.Event import Event, debug
from model.StartEvent import StartEvent
from model.Graph import Graph
import config
#from discrevpy import simulator
from GraphProcessor import GraphProcessor
import subprocess
import sys
import pdb

processor = GraphProcessor()
print("Test cho file 2ndSimple.txt")
processor.printOut = False
filepath = "2ndSimple.txt"
processor.process_input_file(filepath)
processor.H = 10
processor.generate_hm_matrix()
processor.d = 1
processor.generate_adj_matrix()
processor.create_tsg_file()
count = 0
while(count <= 1):
    processor.ID = 3
    processor.earliness = 4 if count == 0 else 7
    processor.tardiness = 6 if count == 0 else 9
    processor.alpha = 1
    processor.beta = 1
    processor.add_time_windows_constraints()
    assert len(processor.tsEdges) == len(processor.ts_edges), f"Thiếu cạnh ở đâu đó rồi {len(processor.tsEdges)} != {len(processor.ts_edges)}"
    count += 1
#processor.update_tsg_with_T()
#processor.add_restrictions()
processor.gamma = 1
processor.restriction_count = 1
processor.startBan = 0
processor.endBan = 2
processor.restrictions = [[2, 3]]
processor.Ur = 1
processor.startedNodes = [1, 10]
processor.process_restrictions()

#realTime = int(input("Thời gian thực tế: "))
#predictedChange = int(input("Sự thay đổi thời gian dự kiến của các cạnh còn lại: "))

graph = Graph()
"""for edge in processor.ts_edges:
    start = edge.start_node
    end = edge.end_node
    graph.insertEdgesAndNodes(start, end, edge)"""

processor.init_nodes_n_edges(graph)
assert (graph.count_edges() == len(processor.ts_edges)), "Missing some edges elsewhere"
#pdb.set_trace()
assert (len(graph.nodes) == len(processor.ts_nodes)), f"Missing some nodes elsewhere as {len(graph.nodes)} != {len(processor.ts_nodes)}"

graph.update(currentpos = 1, nextpos = 8, realtime = 3)
#graph.update_file(id1 = 1, id2 = 8, c12 = 3)

