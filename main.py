from model.Graph import Graph#, graph
from model.AGV import AGV
from model.Event import Event, debug
from model.StartEvent import StartEvent
import config
from discrevpy import simulator
from GraphProcessor import GraphProcessor
import subprocess
import sys
import pdb

def getForecast():
    return 17

allAGVs = set()
TASKS = set()

x = {}
y = {}

pre_processor = GraphProcessor()
pre_processor.use_in_main(False)

graph = Graph()  # Assuming a Graph class has appropriate methods to handle updates

events = []
Event.setValue("numberOfNodesInSpaceGraph", pre_processor.M) #sẽ phải đọc file Edges.txt để biết giá trị cụ thể
Event.setValue("debug", 0)
# Kiểm tra xem có tham số nào được truyền qua dòng lệnh không
if len(sys.argv) > 1:
    Event.setValue("debug", 1 if sys.argv[1] == '-g' else 0)

numberOfNodesInSpaceGraph = Event.getValue("numberOfNodesInSpaceGraph")
# Mở file để đọc

pre_processor.init_AGVs_n_events(allAGVs, events, graph)
pre_processor.init_TASKs(TASKS)
pre_processor.init_nodes_n_edges(graph)
assert (graph.count_edges() == len(pre_processor.ts_edges)), "Missing some edges elsewhere"
pdb.set_trace()
assert (len(graph.nodes) == len(pre_processor.ts_nodes)), f"Missing some nodes elsewhere as {len(graph.nodes)} != {len(pre_processor.ts_nodes)}"


with open('TSG_0.txt', 'r') as f:
    # Đọc từng dòng của file
    for line in f:
        # Phân tích dòng thành các phần tử, phân tách bởi khoảng trắng
        parts = line.split()
        # Kiểm tra loại dữ liệu của dòng
        if parts[0] == 'n':  # Nếu là dòng chứa thông tin về AGV hoặc công việc
            if int(parts[2]) == 1:
                pass
            elif int(parts[2]) == -1:
                #TASKS.add(parts[1])  # Thêm vào tập hợp TASKS
                pass
            elif parts[0] == 'a':  # Nếu là dòng chứa thông tin về mối quan hệ
                #i, j, c_i_j = int(parts[1]), int(parts[2]), int(parts[5])
                #x[i, j] = c_i_j  # Lưu thông tin về mối quan hệ vào từ điển x
                #graph.insertEdgesAndNodes(i, j, c_i_j)
                pass

events = sorted(events, key=lambda x: x.startTime)
Event.setValue("allAGVs", allAGVs)

"""def parse_tsg_file(filename):
    events = []
    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if parts[0] == 'n' and int(parts[2]) == 1:  # Assuming '1' signifies a starting condition
                node_id = int(parts[1])
                agv = AGV("AGV" + str(node_id), node_id)  # Create an AGV at this node
                start_event = StartEvent(0, agv, graph)  # Start event at time 0
                events.append(start_event)
                # We could potentially break here if we only expect one starting event or continue if multiple starts are possible
    return sorted(events, key=lambda x: x.startTime)
"""

def schedule_events(events):
    for event in events:
        simulator.schedule(event.startTime, event.process)

def choose_solver():
    print("Choose the method for solving:")
    print("1 - Use LINK II solver")
    print("2 - Use network-simplex")
    choice = input("Enter your choice (1 or 2): ")
    if choice == '1':
        config.solver_choice = 'solver'
    elif choice == '2':
        config.solver_choice = 'network-simplex'
    else:
        print("Invalid choice. Defaulting to network-simplex.")
        config.solver_choice = 'network-simplex'

if __name__ == "__main__":
    simulator.ready()
    #events = parse_tsg_file('TSG_0.txt')
    choose_solver()
    schedule_events(events)
    simulator.run()
