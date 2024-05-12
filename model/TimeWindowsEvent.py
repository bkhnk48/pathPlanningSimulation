from .Event import Event
class TimeWindowsEvent(Event):
    def __init__(self, startTime, endTime, agv, graph, target_node):
        super().__init__(startTime, endTime, agv, graph)
        self.target_node = target_node  # Mục tiêu mà AGV phải đạt đến trong một khoảng thời gian nhất định

    def calculateCost(self):
        # Chi phí dựa trên trọng số của cung mà AGV đi trên đồ thị TSG
        edge = self.graph.get_edge(self.agv.current_node, self.target_node)
        if edge:
            cost_increase = edge.weight
            self.agv.cost += cost_increase  # Cập nhật chi phí của AGV
            print(
                f"Cost increased by {cost_increase} for AGV {self.agv.id} due to TimeWindowsEvent at {self.target_node}"
            )
        else:
            print("No edge found or incorrect edge weight.")

    def getNext(self):
        # Tính toán chi phí
        self.calculateCost()
        # Có thể thực hiện các hành động tiếp theo tùy thuộc vào logic của bạn
        # Ví dụ: kiểm tra xem có sự kiện tiếp theo cần được lên lịch không

    def process(self):
        # Xử lý khi sự kiện được gọi
        print(
            f"AGV {self.agv.id} processes TimeWindowsEvent at {self.target_node} at time {self.endTime}"
        )
        self.getNext(self.graph)



