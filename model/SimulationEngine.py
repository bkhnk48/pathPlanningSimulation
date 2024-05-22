import heapq  # Using heapq to manage a priority queue
from discrevpy.simulator import Simulator
from model.Graph import Graph
from model.AGV import AGV
from model.Event import MovingEvent, HoldingEvent
from model.Edge import Edge
from model.Node import Node

class SimulationEngine:
    def __init__(self, graph):
        self.graph = graph # Assuming Graph class is already implemented
        self.agvs = []  # List to store all AGVs
        self.simulator = Simulator()  # discrevpy Simulator instance
        self.current_time = 0.0
        
    def load_graph(self):
        # Load the graph from a file or another source
        # Example: Read nodes and edges from a TSG.txt file
        with open("TSG.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                parts = line.split()
                if parts[0] == 'a':  # edges
                    start, end, _, _, weight = map(int, parts[1:6])
                    self.graph.add_edge(Edge(start, end, weight))
                elif parts[0] == 'n':  # nodes
                    node_id, agv_present = map(int, parts[1:])
                    node = Node(node_id)
                    self.graph.add_node(node)
                    if agv_present == 1:
                        self.agvs.append(AGV(len(self.agvs) + 1, node))
                        
    def place_agvs(self):
        # Place AGVs on their starting nodes if not already handled in load_graph
        pass
    
    def preprocess_data(self):
        # Any additional preprocessing needed before the simulation starts
        pass
    
    def run(self):
        # Start the simulation
        self.simulator.run()

    def schedule_event(self, time, event_function, *args):
        # Schedule an event
        self.simulator.schedule(time, event_function, *args)

    def process_event(self, event):
        # Process events as they come
        # You would typically call this method from within event-related methods or callbacks
        if isinstance(event, MovingEvent):
            event.agv.move_to(event.target_node)
        elif isinstance(event, HoldingEvent):
            event.agv.wait(event.duration)
        # Add logic for processing other types of events
        print(f"Processed event: {event}")
        
    def update_graph(self, start_node, end_node, weight):
        self.graph.update_graph(start_node, end_node, weight)