from .Event import Event
import pdb
class ReachingTargetEvent(Event):
    def __init__(self, startTime, endTime, agv, graph, target_node):
        super().__init__(startTime, endTime, agv, graph)
        self.target_node = target_node
        pdb.set_trace()
        node = self.graph.nodes[target_node]
        M = self.graph.numberOfNodesInSpaceGraph
        time = self.agv.current_node // M \
            - (1 if self.agv.current_node % M == 0 else 0)
        pdb.set_trace()
        if not hasattr(node, 'earliness'):
            try:
                node = next(node for node in self.graph.graph_processor.getTargets() if node.id == target_node)
                #print(f"Đối tượng Node với id {target_id} được tìm thấy.")
                self.graph.nodes[target_node] = node
            except StopIteration:
                print(f"Không tìm thấy đối tượng Node với id {target_node}.")
                pdb.set_trace()
        earliness = node.earliness
        tardiness = node.tardiness
        self.last_cost = self.graph.graph_processor.beta*(max([earliness - time, 0, time - tardiness]))/self.graph.graph_processor.alpha
        #self.last_cost = self.graph.get_edge(self.agv.current_node, self.target_node)
        """for node, earliness, tardiness in \
            self.graph.graph_processor.time_window_controller.TWEdges[self.agv.current_node]:
                if(node == self.target_node):
                    M = self.graph.numberOfNodesInSpaceGraph
                    time = self.agv.current_node // M \
                        - (1 if self.agv.current_node % M == 1 else 0)
                    cost = self.graph.beta*(max([earliness - time, 0, time - tardiness]))
                    self.last_cost = cost
                    break"""
        if(self.graph.graph_processor.printOut):
            print(f"Last cost: {self.last_cost}")

    def updateGraph(self):
        # Không làm gì cả, vì đây là sự kiện đạt đến mục tiêu
        self.graph.remove_node_and_origins(self.target_node)

    def calculateCost(self):
        # Retrieve the weight of the last edge traversed by the AGV
        if self.agv.previous_node is not None and self.target_node is not None:
            #last_edge_weight = self.graph.get_edge(self.agv.current_node, self.target_node)
            last_edge_weight = self.last_cost
            if last_edge_weight is not None:
                # Calculate cost based on the weight of the last edge
                cost_increase = last_edge_weight
                self.agv.update_cost(cost_increase)
                if(self.graph.graph_processor.printOut):
                    print(
                        f"Cost for reaching target node {self.target_node} is based on last edge weight: {cost_increase}."
                    )
            else:
                if(self.graph.graph_processor.printOut):
                    print("No last edge found; no cost added.")
        else:
            if(self.graph.graph_processor.printOut):
                print("Previous node or target node not set; no cost calculated.")
        return self.agv.cost

    def process(self):
        if(self.graph.graph_processor.printOut):
            # Đây là phương thức để xử lý khi AGV đạt đến mục tiêu
            print(
                f"AGV {self.agv.id} has reached the target node {self.target_node} at time {self.endTime}"
                )
        #pdb.set_trace()
        print(self.agv.path)
        cost = self.calculateCost()  # Calculate and update the cost of reaching the target
        #print("DSFFDdsfsdDF")
        print(f"The total cost of {self.agv.id} is {cost}")
        self.updateGraph()  # Optional: update the graph if necessary
