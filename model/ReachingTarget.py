from .Event import Event
class ReachingTarget(Event):
    def __init__(self, startTime, endTime, agv, graph, target_node):
        super().__init__(startTime, endTime, agv, graph)
        self.target_node = target_node

    def updateGraph(self):
        # Không làm gì cả, vì đây là sự kiện đạt đến mục tiêu
        pass

    def calculateCost(self):
        # Retrieve the weight of the last edge traversed by the AGV
        if self.previous_node is not None and self.target_node is not None:
            last_edge_weight = self.graph.get_edge(self.agv.previous_node, self.target_node)
            if last_edge_weight is not None:
                # Calculate cost based on the weight of the last edge
                cost_increase = last_edge_weight
                self.agv.update_cost(cost_increase)
                print(
                    f"Cost for reaching target node {self.target_node} is based on last edge weight: {cost_increase}."
                )
            else:
                print("No last edge found; no cost added.")
        else:
            print("Previous node or target node not set; no cost calculated.")

    def process(self):
        # Đây là phương thức để xử lý khi AGV đạt đến mục tiêu
        print(
            f"AGV {self.agv.id} has reached the target node {self.target_node} at time {self.endTime}"
        )
        self.calculateCost()  # Calculate and update the cost of reaching the target
        self.updateGraph(self.graph)  # Optional: update the graph if necessary
