from model.Graph import Graph#, graph
from model.AGV import AGV
from model.Event import Event, debug
from model.StartEvent import StartEvent
from model.Graph import Graph
from model.TimeWindowNode import TimeWindowNode
from model.RestrictionNode import RestrictionNode
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

graph = Graph(processor)
"""for edge in processor.ts_edges:
    start = edge.start_node
    end = edge.end_node
    graph.insertEdgesAndNodes(start, end, edge)"""

pdb.set_trace()
processor.init_nodes_n_edges(graph)
assert (graph.count_edges() == len(processor.ts_edges)), "Missing some edges elsewhere"
assert (len(graph.nodes) == len(processor.ts_nodes)), f"Missing some nodes elsewhere as {len(graph.nodes)} != {len(processor.ts_nodes)}"

id1 = 1
id2 = 8
c12 = 3
processor.update_file(id1, id2, c12)
current_time = id1 // processor.M + c12
pdb.set_trace()

for node in graph.nodes.values():
    if not isinstance(node, (TimeWindowNode, RestrictionNode)):
        time = node.id / graph.numberOfNodesInSpaceGraph
        assert (time >= current_time) == 24, "Assertion failed for node with id {}".format(node.id)

""" Cần có các assert như sau:
(1) Tất cả các Node (không kể các TimeWindowNode và RestrictionNode) mà có time >= thời điểm hiện tại* thì bằng 24
(2) Tất cả các Edge (không kể các TimeWindowEdge và RestrictionEdge) thì đỉnh nguồn của chúng phải có time >= thời điểm hiện tại*
(3) Tất cả các TimeWindowNode thì vẫn còn các đỉnh khác nối đến chúng
(4) Tất cả các RestrictionNode thì vẫn còn đỉnh nối đến chúng
(5) Số các TimeWindowNode sẽ bằng 2
(6) Số các TimeWindowEdge mới sẽ bằng số TimeWindowsEdge cũ trừ đi số TimeWindowEdge có đỉnh nguồn với thời điểm của đỉnh nguồn < thời điểm hiện tại
(7) Số các RestrictionEdge mới (có đỉnh nguồn không phải RestrictionNode) sẽ bằng số
     RestrictionEdge (có đỉnh nguồn không phải RestrictionNode) cũ trừ đi 
     số RestrictionEdge có đỉnh nguồn (không phải RestrictionNode) với thời điểm của đỉnh nguồn < thời điểm hiện tại
(8) Số các RestrictionEdge mới (có đỉnh đích không phải RestrictionNode) sẽ bằng số
     RestrictionEdge (có đỉnh đích không phải RestrictionNode) cũ trừ đi 
     số RestrictionEdge có đỉnh đích (không phải RestrictionNode) với thời điểm của đỉnh đích < thời điểm hiện tại     
*thời điểm hiện tại: có công thức tính thời điểm hiện tại từ tham số của hàm update_file 
"""
#graph.update(currentpos = 1, nextpos = 8, realtime = 3)
#graph.update_file(id1 = 1, id2 = 8, c12 = 3)

