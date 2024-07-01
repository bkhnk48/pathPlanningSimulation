from model.Graph import Graph#, graph
from model.AGV import AGV
from model.Event import Event, debug
from model.StartEvent import StartEvent
import config
from discrevpy import simulator
from collections import deque
from GraphProcessor import GraphProcessor
from model.ReachingTargetEvent import ReachingTargetEvent
import subprocess
import sys
import pdb

def getForecast():
    return 17

allAGVs = set()
TASKS = set()

x = {}
y = {}

graph_processor = GraphProcessor()
graph_processor.use_in_main()
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

def new_schedule_events(events):

    Q = deque()
    for event in events:
        Q.append(event)
        #simulator.schedule(event.startTime, event.process)
    while Q:
        event = Q.popleft()
        simulator.schedule(event.startTime, event.process)
        if not isinstance(event,ReachingTargetEvent):
            Q.append(event.getNext())



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
    new_schedule_events(events)
    simulator.run()
