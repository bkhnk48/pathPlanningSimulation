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
import time

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
def getForecast():
    return 17

allAGVs = set()
TASKS = set()

x = {}
y = {}

choose_solver()
graph_processor = GraphProcessor()
start_time = time.time()
graph_processor.use_in_main()
end_time = time.time()
# Tính thời gian thực thi
execution_time = end_time - start_time
if(execution_time >= 5):
    print(f"Thời gian thực thi: {execution_time} giây")
graph_processor.printOut = False

graph = Graph(graph_processor)  # Assuming a Graph class has appropriate methods to handle updates

events = []
Event.setValue("numberOfNodesInSpaceGraph", graph_processor.M) #sẽ phải đọc file Edges.txt để biết giá trị cụ thể
Event.setValue("debug", 0)
# Kiểm tra xem có tham số nào được truyền qua dòng lệnh không
if len(sys.argv) > 1:
    Event.setValue("debug", 1 if sys.argv[1] == '-g' else 0)

numberOfNodesInSpaceGraph = Event.getValue("numberOfNodesInSpaceGraph")
# Mở file để đọc
graph_processor.init_AGVs_n_events(allAGVs, events, graph)
graph_processor.init_TASKs(TASKS)
graph_processor.init_nodes_n_edges(graph)
# assert (graph.count_edges() == len(graph_processor.ts_edges)), "Missing some edges elsewhere"
# #pdb.set_trace()
# assert (len(graph.nodes) == len(graph_processor.ts_nodes)), f"Missing some nodes elsewhere as {len(graph.nodes)} != {len(graph_processor.ts_nodes)}"

events = sorted(events, key=lambda x: x.startTime)
Event.setValue("allAGVs", allAGVs)


def schedule_events(events):
    for event in events:
        #pdb.set_trace()
        simulator.schedule(event.startTime, event.process)

if __name__ == "__main__":
    simulator.ready()
    #events = parse_tsg_file('TSG_0.txt')
    schedule_events(events)
    simulator.run()
