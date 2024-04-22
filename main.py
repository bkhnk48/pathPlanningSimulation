from model.Graph import Graph
from model.AGV import AGV
from model.Event import HoldingEvent, StartEvent
from discrevpy import simulator
import subprocess
def getReal():
    return 15

def getForecast():
    return 17

AGV = set()
TASKS = set()

x = {}
y = {}

graph = Graph()  # Assuming a Graph class has appropriate methods to handle updates

# Mở file để đọc
with open('TSG_0.txt', 'r') as f:
	# Đọc từng dòng của file
	for line in f:
    	# Phân tích dòng thành các phần tử, phân tách bởi khoảng trắng
            parts = line.split()
    	# Kiểm tra loại dữ liệu của dòng
            if parts[0] == 'n':  # Nếu là dòng chứa thông tin về AGV hoặc công việc
                if int(parts[2]) == 1:
                    AGV.add(parts[1])  # Thêm vào tập hợp AGV
                elif int(parts[2]) == -1:
                    TASKS.add(parts[1])  # Thêm vào tập hợp TASKS
            elif parts[0] == 'a':  # Nếu là dòng chứa thông tin về mối quan hệ
                    i, j, c_i_j = int(parts[1]), int(parts[2]), int(parts[5])
                    x[i, j] = c_i_j  # Lưu thông tin về mối quan hệ vào từ điển x
            graph.insertEdgesAndNodes(i, j, c_i_j)

def parse_tsg_file(filename):
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

def schedule_events(events):
    for event in events:
        simulator.schedule(event.startTime, event.process)

# Main execution
if __name__ == "__main__":
    simulator.ready()
    events = parse_tsg_file('TSG_0.txt')
    schedule_events(events)
    simulator.run()
