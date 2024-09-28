import os
import pdb
from collections import deque, defaultdict
from .utility import utility
import inspect
from .RestrictionNode import RestrictionNode
from .TimeWindowNode import TimeWindowNode
from .TimeoutNode import TimeoutNode
from .Node import Node
import config
from .hallway_simulator_module.HallwaySimulator import BulkHallwaySimulator

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
class Graph:
    def __init__(self, graph_processor):
        self.graph_processor = graph_processor 
        self.adjacency_list = defaultdict(list)
        self.nodes = {node.id: node for node in graph_processor.ts_nodes}
        self.adjacency_list = {node.id: [] for node in graph_processor.ts_nodes}
        #self.nodes = self.graph_processor.ts_nodes
        #self.lastChangedByAGV = -1
        #self.edges = self.graph_processor.ts_edges
        #self.nodes = {}
        #self.adjacency_list = {}
        self.list1 = []
        self.neighbour_list = {}
        self.visited = set()
        #self.id2_id4_list = []
        self.version = -1
        self.file_path = None
        self.cur = []
        self.map = {}
        self.numberOfNodesInSpaceGraph = -1 if graph_processor is None else graph_processor.M
        self.calling = 0
        self.continueDebugging = True
        #print("Initialized a new graph.")
        #stack = inspect.stack()
        #for frame in stack[1:]:
        #    print(f"Hàm '{frame.function}' được gọi từ file '{frame.filename}' tại dòng {frame.lineno}")
        
    def getReal(self, start_id, next_id, agv):
        result = -1
        from .TimeWindowNode import TimeWindowNode
        M = self.numberOfNodesInSpaceGraph
        if(agv is not None):
            #print(f'{agv.id}')
            #pdb.set_trace()
            old_real_path = [(node % M + (M if node % M == 0 else 0)) for node in agv.path]
            real_start_id = start_id % M + (M if start_id % M == 0 else 0)
            for real_node in old_real_path:
                if(real_start_id == real_node):
                    #pdb.set_trace()
                    break
            agv.path.add(start_id)
        startTime = start_id // M - (1 if start_id % M == 0 else 0)
        endTime = next_id // M - (1 if next_id % M == 0 else 0)
        space_start_node = start_id % M + (M if start_id % M == 0 else 0)
        space_end_node = next_id % M + (M if next_id % M == 0 else 0)
        edges_with_cost = { (int(edge[1]), int(edge[2])): [int(edge[4]), int(edge[5])] for edge in self.graph_processor.spaceEdges \
            if edge[3] == '0' and int(edge[4]) >= 1 }
        min_moving_time = edges_with_cost.get((space_start_node, space_end_node), [-1, -1])[1]
        endTime = max(endTime, startTime + min_moving_time)
        allIDsOfTargetNodes = [node.id for node in self.graph_processor.targetNodes]
        if(next_id in allIDsOfTargetNodes):
            #pdb.set_trace()
            if(agv is not None):
                agv.path.add(next_id)
            result = 0
        try:
            if isinstance(self.nodes[next_id], TimeWindowNode):
                #pdb.set_trace()
                result = (endTime - startTime) if result == -1 else result
        except:
            if next_id not in self.nodes:
                #print(f'in self.nodes doesnt have {next_id}')
                for e in self.graph_processor.tsEdges:
                    if(e[0] % M == start_id % M and e[1] % M == next_id % M):
                        #pdb.set_trace()
                        result = e[4] if result == -1 else result
                #pdb.set_trace()
                result = abs(endTime - startTime) if result == -1 else result
        #pdb.set_trace()

        if config.useSFM == True:
            print(f"Using sfm for AGV {agv.id} from {start_id} to {next_id} at time {startTime}.")
            result = self.getAGVRuntime(config.filepath, config.functions_file, space_start_node, space_end_node, agv, startTime)
            if result != -1:
                return result

        result = (3 if (endTime - startTime <= 3) else 2*(endTime - startTime) - 3) if result == -1 else result
        collision = True
        #pdb.set_trace()
        while(collision):
            collision = False
            if (next_id not in allIDsOfTargetNodes):
                if(next_id in self.nodes.keys()):
                    if(self.nodes[next_id].agv is not None):
                        if(self.nodes[next_id].agv != agv):
                            print(f'{self.nodes[next_id].agv.id} != {agv.id}')
                            #pdb.set_trace()
                            collision = True
                            result = result + 1
                            next_id = next_id + M
            
        return result
    

#=======================================================================================================
# Huy code
    def getReal_preprocess(self, Map_file, function_file):
        # read 2 files Map_file(txt) and function_file(txt)
        """
        Map_file: a <src> <dest> <low> <cap> <cost> <hallway_id> <human_distribution_percentage>
        if src < dest: left to right
        if src > dest: right to left
        a 1 2 0 1 1 Region_1 3
        a 3 2 0 1 1 Region_1 4
        a 1 4 0 1 1 Region_2 5
        a 5 4 0 1 1 Region_2 3
        ...
        """
        """
        function_file: each line
        y = 34 * x + 32 (0,50)
        y = 3 * x + -100 (60,500)
        """
        # read files
        map_data = None
        function_data = None
        with open(Map_file, 'r', encoding='utf-8') as file:
            map_data = file.readlines()
        with open(function_file, 'r', encoding='utf-8') as file:
            function_data = file.readlines()
        # process data
        """
        hallways_list = [
            {
                "hallway_id": "Region_1",
                "length": 66, # change base on cost * 0.6
                "width": 4, # constant default to 4
                "agents_distribution": 15
            },
            {
                "hallway_id": "Region_2",
                "length": 66, # change base on cost * 0.6
                "width": 4, # constant
                "agents_distribution": 12
            }
        ]
        """
        """
        functions_list = [
            "y = 34 * x + 32 (0,50)",
            "y = 3 * x + -100 (60,500)"
        ]
        """
        hallways_list = []
        functions_list = []
        for line in map_data:
            line = line.strip()
            parts = line.split(" ")
            if len(parts) == 8:
                hallway = {
                    "hallway_id": parts[6],
                    "length": int(int(parts[5]) * 0.6),
                    "width": 4,
                    "agents_distribution": int(parts[7]),
                    "src": int(parts[1]),
                    "dest": int(parts[2])
                }
                hallways_list.append(hallway)
        for line in function_data:
            line = line.strip()
            functions_list.append(line)
        return hallways_list, functions_list

    def getAGVRuntime(self, Map_file, function_file, start_id, next_id, agv, current_time):
        hallways_list, functions_list = self.getReal_preprocess(Map_file, function_file)
        events_list = []  # actually only has one event but because of the structure of the code, it has to be a list
        """
        {
            "AgvIDs": [0], # depends
            "AgvDirections": [0], # depends
            "time_stamp": 0, # depends
            "hallway_id": "hallway_1" # depends
        }
        """
        # get the agv id from the agv object id: AGV1 -> 1
        agv_id = int(agv.id[3:])
        # get the direction of the agv by querying the hallways_list with the start_id and next_id
        direction = 0
        for hallway in hallways_list:
            if hallway["src"] == start_id and hallway["dest"] == next_id:
                direction = 1
                hallway_id = hallway["hallway_id"]
                break
            elif hallway["src"] == next_id and hallway["dest"] == start_id:
                direction = -1
                hallway_id = hallway["hallway_id"]
                break
            else:
                hallway_id = None
        
        # get the time_stamp from the current_time
        time_stamp = current_time

        # if hallway_id is not found, return -1
        if hallway_id is None:
            # just pass this entire function
            print(f"{bcolors.WARNING}Hallway not found!{bcolors.ENDC}")
            return -1

        # add to json
        event = {
            "AgvIDs": [agv_id],
            "AgvDirections": [direction],
            "time_stamp": time_stamp,
            "hallway_id": hallway_id
        }
        events_list.append(event)

        # filter the hallways_list to only have the hallway that the agv is currently in
        hallways_list = [hallway for hallway in hallways_list if event["hallway_id"] == hallway_id and (hallway["src"] - hallway["dest"]) * direction > 0]

        print(hallways_list)
        print(functions_list)
        print(events_list)

        bulk_sim = BulkHallwaySimulator("test", 3600, hallways_list, functions_list, events_list)
        result = bulk_sim.run_simulation()
        # result will look like this: {0: {'hallway_1': {'time_stamp': 0, 'completion_time': 111}}, 1: {'hallway_1': {'time_stamp': 0, 'completion_time': 111}}}
        # get the completion_time from the result
        completion_time = result[agv_id][hallway_id]["completion_time"]
        return completion_time # int
#=======================================================================================================



    
    def count_edges(self):
        count = 0
        for node in self.adjacency_list:
            count = count + len(self.adjacency_list[node])
        return count
            
    """def insertEdgesAndNodes(self, start_id, end_id, edge):
        self.adjacency_list[start_id].append((end_id, edge))
        #self.ensure_node_capacity(start_id)
        #self.ensure_node_capacity(end_id)
        if self.nodes[start_id] is None:
            self.nodes[start_id] = {'id': start_id}
        if self.nodes[end_id] is None:
            self.nodes[end_id] = {'id': end_id}"""
    def insertEdgesAndNodes(self, start, end, edge):
        from .Node import Node
        start_id = start if isinstance(start, int) else start.id
        end_id = end if isinstance(end, int) else end.id
        self.adjacency_list[start_id].append((end_id, edge))
        #self.ensure_node_capacity(start_id)
        #self.ensure_node_capacity(end_id)
        start_node = start if isinstance(start, Node) else self.graph_processor.find_node(start)
        end_node = end if isinstance(end, Node) else self.graph_processor.find_node(end)
        if self.nodes[start_id] is None:
            self.nodes[start_id] = start_node
        if self.nodes[end_id] is None:
            self.nodes[end_id] = end_node
    
    def find_unique_nodes(self, file_path = 'traces.txt'):
        """ Find nodes that are only listed as starting nodes in edges. """
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return []
        
        target_ids = set()
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line.startswith('a'):
                    parts = line.split()
                    target_ids.add(int(parts[3]))

        unique_ids = set()
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line.startswith('a'):
                    parts = line.split()
                    node_id = int(parts[1])
                    if node_id not in target_ids:
                        unique_ids.add(node_id)

        return list(unique_ids)
    
    def find_unpredicted_node(self, id, forceFinding = False, isTargetNode = False):
        node = None
        idIsAvailable = id in self.nodes
        if idIsAvailable and not forceFinding:
            node = self.nodes[id]
        else:
            #if start == -1:
            found = False
            M = self.numberOfNodesInSpaceGraph
            for x in self.nodes:
                if(x % M == id % M and (self.nodes[x].agv is not None or isTargetNode)):
                    if(idIsAvailable):
                        if(type(self.nodes[x]) == type(self.nodes[id])):
                            found = True
                    elif(isinstance(self.nodes[x], Node)\
                                and not isinstance(self.nodes[x], TimeWindowNode)\
                                    and not isinstance(self.nodes[x], RestrictionNode)):
                        found = True
                    if(found):
                        node = self.nodes[x]
                        break
        return node
        
    def build_path_tree(self, file_path = 'traces.txt'):
        """ Build a tree from edges listed in a file for path finding. """
        #pdb.set_trace()
        id1_id3_tree = defaultdict(list)
        M = self.numberOfNodesInSpaceGraph
        #start = -1
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line.startswith('a'):
                    numbers = line.split()
                    id1 = int(numbers[1])
                    #if(id1 == 32):
                    #    pdb.set_trace()
                    #    #pass
                    id3 = int(numbers[2])
                    id2 = id1 % M
                    id4 = id3 % M
                    node1 = self.find_unpredicted_node(id1) 
                    if (node1 is not None):
                        #pdb.set_trace()
                        isTargetNode = True
                        node3 = self.find_unpredicted_node(id3, node1.id != id1, isTargetNode)
                        #node2 = self.nodes[id2]
                        if(node3 is None):
                            print(f"{node1.id}/{id1} {id3}")
                        id3 = node3.id
                        self.neighbour_list[id1] = id2
                        self.neighbour_list[id3] = id4
                        #print(self.graph_processor.startedNodes)
                        #pdb.set_trace()
                        if(node1.id in self.graph_processor.startedNodes or\
                            node1.agv is not None):
                            #pdb.set_trace()
                            self.list1.append(node1.id)
                        id1_id3_tree[node1.id].append(node3)
                        id1_id3_tree[id3].append(node1)
        return id1_id3_tree

    def dfs(self, tree, start_node):
        self.visited.add(start_node)
        for node in tree[start_node]:
            node_id = node if isinstance(node, int) else node.id
            if node_id not in self.visited:
                #print(node, end=' ')
                self.cur.append(node)
                #self.id2_id4_list.append(self.neighbour_list[node_id])
                self.dfs(tree, node_id)

    def setTrace(self, file_path = 'traces.txt'):
        #pdb.set_trace()
        self.file_path = file_path #'traces.txt'
        self.list1 = []
        self.neighbour_list = {}
        self.visited = set()
        #self.id2_id4_list = []
        self.map = {}
        edges_with_cost = { (int(edge[1]), int(edge[2])): [int(edge[4]), int(edge[5])] for edge in self.graph_processor.spaceEdges \
            if edge[3] == '0' and int(edge[4]) >= 1 }
        M = self.graph_processor.M
        #pdb.set_trace()
        #unique_numbers = self.find_unique_numbers()
        #unique_numbers = self.find_unique_nodes()
        #print(unique_numbers)
        #id1_id3_tree = self.create_trees()
        id1_id3_tree = self.build_path_tree()#self.list1 sẽ được thay đổi ở đâyđây
        for number in self.list1:
            if number not in self.visited:
                #print(number, end=' ')
                #self.id2_id4_list.append(self.neighbour_list[number])
                self.cur = []
                self.dfs(id1_id3_tree, number)
                self.visited = set()
                if len(self.cur) >= 1:
                    start = number % M + (M if number % M == 0 else 0)
                    end = self.cur[0].id % M + (M if self.cur[0].id % M == 0 else 0)
                    start_time = number // M - (1 if number % M == 0 else 0)
                    end_time = self.cur[0].id // M - (1 if self.cur[0].id % M == 0 else 0)
                    min_cost = edges_with_cost.get((start, end), [-1, -1])[1]
                    if(min_cost == -1):
                        need_to_remove_first_cur = True
                        if(start == end and number != self.cur[0].id and end_time - start_time == self.graph_processor.d):
                            need_to_remove_first_cur = False
                        #if(isinstance(self.cur[0], TimeWindowNode) or len(self.cur) == 1):
                        #    pdb.set_trace()
                        #pdb.set_trace()
                        #indices_dict = {source_id: [index for index, e in enumerate(edges) if e[0].id == end]\
                        if need_to_remove_first_cur:
                            found = False
                            for source_id, edges in self.graph_processor.time_window_controller.TWEdges.items():
                                if edges is not None and source_id % M == start:
                                    for index, e in enumerate(edges):
                                        if e[0].id ==end:
                                            found = True
                                            break
                            if(not found):                                    
                                self.cur = self.cur[1:]
                #if(len(self.cur) == 0):
                #    pdb.set_trace()
                self.map[number] = self.cur #[1: ] if len(self.cur) > 1 else self.cur
                #print('#', end=' ')
                #print(' '.join(map(str, id2_id4_list)))
                #self.id2_id4_list = []
        """for item in self.map.keys():
            print(f'\033[4m Graph.py: 234: {item} has trace: \033[0m {self.map[item]}\n')"""
    
    def getTrace(self, agv):
        #pdb.set_trace()
        idOfAGV = int(agv.id[3:])
        #for key, value in self.map.items():
        #    print(f"Key: {key}, Value: {value}")
        """if(len(agv.traces) > 0):
            if(agv.traces[0].id == 27):
                pdb.set_trace()"""
        if idOfAGV in self.map:
            return self.map[idOfAGV]  
        else:
            found = False
            temp = []
            for id in self.nodes:
                if self.nodes[id].agv == agv:
                    #if(id == 13899 or id == 13898):
                    #    pdb.set_trace()
                    if(id not in self.map):
                        for old_id in self.map.keys():
                            if(self.nodes[id].agv == self.nodes[old_id].agv):
                                temp = self.map[old_id]
                                found = True
                                break
                            else:
                                if isinstance(self.map[old_id], list):
                                    for node in self.map[old_id]:
                                        if node.agv == agv:
                                            temp = self.map[old_id]
                                            found = True
                                            break
                            if found:
                                break
                    else:
                        temp = self.map[id]#13899
                        found = True
                    node = self.nodes[id]
                    #if(found == False):
                    #    pdb.set_trace()
                    return [node, *temp]
                    #return s self.map[id]
        return None
    
    def has_initial_movement(self, node):
        # Check if there are any outgoing edges from 'node'
        return node in self.edges and len(self.edges[node]) > 0
    
    def update(self,currentpos,nextpos,realtime):
        list = utility()
        del self.matrix[currentpos,nextpos]
        Q = deque()
        Q.append(nextpos)
        while Q:
            pos = Q[0]
            Q.pop()
            for i in list.findid(pos):
                if (pos,i) in self.matrix:
                    del self.matrix[pos,i]
                    Q.append(i)
        nextpos = list.M*(int(currentpos/list.M)+ realtime) + list.getid(nextpos)
        self.matrix[currentpos,nextpos] = realtime
        Q.append(nextpos)
        while Q:
            pos = Q[0]
            Q.pop()
            for i in list.findid(pos):
                if (pos,i) not in self.matrix:
                    self.matrix[pos,i] = int((pos-i)/list.M)
                    Q.append(i)      
              
    def update_node(self, node, properties):
        #pdb.set_trace()
        #pass
        return
        """if node in self.nodes:
            self.nodes[node].update(properties)
            print(f"Node {node} updated with properties {properties}.")
        else:
            self.nodes[node] = properties
            print(f"Node {node} added with properties {properties}.")"""
 
    def add_edge(self, from_node, to_node, weight):
        self.adjacency_list[from_node].append((to_node, weight))
        print(f"Edge added from {from_node} to {to_node} with weight {weight}.")

    def display_graph(self):
        print("Displaying graph structure:")
        for start_node in self.adjacency_list:
            for end, weight in self.adjacency_list[start_node]:
                print(f"{start_node} -> {end} (Weight: {weight})")
            
    def get_edge(self, start_node, end_node):
        for neighbor, weight in self.adjacency_list[start_node]:
            if neighbor == end_node:
                print(f"Edge found from {start_node} to {end_node} with weight {weight}.")
                return weight
        print(f"No edge found from {start_node} to {end_node}.")
        return None
    
    def find_edge_by_weight(self, start_node, weight):
        # Find all edges from a node with a specific weight
        return [edge for edge in self.edges if edge.start_node == start_node and edge.weight == weight]
    
    def find_path(self, start_node, end_node):
        # Placeholder for a pathfinding algorithm like Dijkstra's
        queue = deque([start_node])
        visited = set()
        path = []
        
        while queue:
            node = queue.popleft()
            if node == end_node:
                break
            visited.add(node)
            for neighbor, weight in self.adjacency_list[node]:
                if neighbor not in visited:
                    queue.append(neighbor)
                    path.append((node, neighbor, weight))
        return path
    
    def update_graph(self, id1 = -1, id2 = -1, end_id = -1, agv_id = None):
    #ý nghĩa của các tham số: id1 - id của nút nguồn X trong đồ thị TSG
    #                         id2 - id cuả nút đích dự kiến Y trong đồ thị TSG
    #                         c12 - thời gian thực tế mà AGV di chuyển từ nút X đến Y
        # Update the graph with new edge information
        #self.add_edge(currentpos, nextpos, realtime)
        ID1 = int(input("Nhap ID1: ")) if id1 == -1 else id1
        ID2 = int(input("Nhap ID2: ")) if id2 == -1 else id2
        endID = int(input("Nhap ID thực sự khi AGV kết thúc hành trình: ")) if end_id == -1 else end_id
        M = self.numberOfNodesInSpaceGraph
        time1, time2 = ID1 // M - (1 if ID1 % M == 0 else 0), ID2 // M - (1 if ID2 % M == 0 else 0)
        #if i2 - i1 != C12:
        #    print('Status: i2 - i1 != C12')
        #    ID2 = ID1 + M * C12
        #existing_edges = set()
        """old_time_window_edges = []
        for source_id, edges in self.adjacency_list.items():
            for destination_id, edge in edges:
                if isinstance(edge, TimeWindowEdge):
                    old_time_window_edges.append(edge)"""
        #current_time = time1 + C12 # Giá trị của current_time
        current_time = endID // M - (1 if endID % M == 0 else 0)
        #if(current_time > self.graph_processor.H):
        #    pdb.set_trace()
        if(current_time >= self.graph_processor.H):
            pdb.set_trace()
        #current_time = current_time if current_time <= self.graph_processor.H else self.graph_processor.H
        new_node_id = current_time*M + (M if ID2 % M == 0 else ID2 % M)
        #if(new_node_id == 13899):
        #    pdb.set_trace()
            
        # Duyệt qua từng phần tử của adjacency_list
        for source_id, edges in list(self.adjacency_list.items()):
            #if(source_id == 51265):
            #    #pdb.set_trace()
            #    pass
            isContinued = False
            for node in self.graph_processor.targetNodes:
                if node.id == source_id:
                    isContinued = True
                    break
            if isContinued:
                continue
            # Tính giá trị time
            if (source_id in self.nodes):
                node = self.nodes[source_id]
                time = source_id // M - (1 if source_id % M == 0 else 0)
                # Nếu time < current_time, not isinstance(node, (TimeWindowNode, RestrictionNode))
                if time < current_time and not isinstance(node, (TimeWindowNode, RestrictionNode)):
                    #if(source_id == 18):
                    # #    pdb.set_trace()allAGVs
                    del self.adjacency_list[source_id]
                    if(self.nodes[source_id].agv is not None):
                        #pdb.set_trace()
                        space_id = M if (source_id % M == 0) else source_id % M
                        new_source_id = current_time*M + space_id
                        try:
                            if new_source_id in self.nodes:
                                self.nodes[new_source_id].agv = self.nodes[source_id].agv
                            index = self.graph_processor.startedNodes.index(source_id)  # Tìm vị trí của phần tử x
                            self.graph_processor.startedNodes[index] = new_source_id  # Thay thế phần tử x bằng phần tử y
                        except ValueError:
                            #print(f"Phần tử {source_id} không tồn tại trong danh sách.")
                            pass
                        #pdb.set_trace()
                    del self.nodes[source_id]
        
        Q = deque()
        Q.append(new_node_id)
        new_started_nodes = self.getAllNewStartedNodes()
        for start in new_started_nodes:
            if(start != new_node_id):
                Q.append(start)
        new_edges = self.graph_processor.insert_from_queue(Q, self.adjacency_list)
        for edge in new_edges:
            arr = self.parse_string(edge)
            source_id = arr[0]
            dest_id = arr[1]
            if source_id not in self.nodes:
                self.nodes[source_id] = self.graph_processor.find_node(source_id)
            if dest_id not in self.nodes:
                self.nodes[dest_id] = self.graph_processor.find_node(dest_id)
            if source_id not in self.adjacency_list:
                self.adjacency_list[source_id] = []
            found = False
            for end_id, e in self.adjacency_list[source_id]:
                if(end_id == dest_id):
                    found = True
                    break
            if(not found):
                anEdge = self.nodes[source_id].create_edge(self.nodes[dest_id], \
                        self.graph_processor.M, self.graph_processor.d, [source_id, \
                        dest_id, arr[2], arr[3], arr[4]])
                self.adjacency_list[source_id].append([dest_id, anEdge])
            
            #add TimeWindowEdge
            self.graph_processor.time_window_controller.generate_time_window_edges(\
                self.nodes[source_id], self.adjacency_list, self.numberOfNodesInSpaceGraph)
            
            self.graph_processor.restriction_controller.generate_restriction_edges(\
                self.nodes[source_id], self.nodes[dest_id], self.nodes, self.adjacency_list)
        if(time2 != current_time):
            #Kể cả không có thêm cạnh mới
            #thì việc đến điểm lệch đi so với dự đoán cũng có thể đồ thị phải cập nhật rồi
            #pdb.set_trace()
            self.version = self.version + 1
        sorted_edges = sorted(self.adjacency_list.items(), key=lambda x: x[0])
        new_nodes = set()
        new_halting_edges = []
        for source_id, edges in sorted_edges:
            for edge in edges:
                t = edge[0] // self.graph_processor.M - (1 if edge[0] % self.graph_processor.M == 0 else 0)
                if(t >= self.graph_processor.H and edge[0] not in new_nodes and isinstance(self.nodes[edge[0]], TimeoutNode)):
                    new_nodes.add(edge[0])
                    L = len(self.graph_processor.getTargets())
                    if(L == 0):
                        pdb.set_trace()
                        targets = self.graph_processor.getTargets()
                    for target in self.graph_processor.getTargets():
                        dest_id = target.id
                        """anEdge = self.nodes[edge[0]].create_edge(self.nodes[dest_id], \
                            self.graph_processor.M, self.graph_processor.d, [edge[0], \
                                dest_id, 0, 1, self.H*self.H])
                        self.adjacency_list[edge[0]].append([dest_id, anEdge])"""
                        new_halting_edges.append([edge[0], dest_id, 0, 1, self.graph_processor.H*self.graph_processor.H])
                """if(t >= self.graph_processor.H):
                    if(edge[0] == 19685):
                        pdb.set_trace()"""
        #pdb.set_trace()
        self.write_to_file([agv_id, new_node_id], new_halting_edges)
        #pdb.set_trace()
        """for node in self.graph_processor.ts_nodes:
            if node.id not in self.nodes:
                self.nodes[node.id] = node
        
        for edge in self.graph_processor.ts_edges:
            source_id = edge.start_node.id
            end_id = edge.end_node.id
            if source_id not in self.adjacency_list or [end_id, edge] not in self.adjacency_list[source_id]:
                if source_id not in self.adjacency_list:
                    self.adjacency_list[source_id] = []
                self.adjacency_list[source_id].append([end_id, edge])
        
        self.write_to_file()"""

    def reset_agv(self, real_node_id, agv):
        for node_id in self.nodes.keys():
            if(node_id != real_node_id):
                if self.nodes[node_id].agv == agv:
                    self.nodes[node_id].agv = None
        self.nodes[real_node_id].agv = agv
    
    def parse_string(self, input_string):
        parts = input_string.split()
        if len(parts) != 6 or parts[0] != "a":
            return None  # Chuỗi không đúng định dạng
        try:
            ID1, ID2, L, U, C = map(int, parts[1:])
            return [ID1, ID2, L, U, C]
        except ValueError:
            return None  # Không thể chuyển thành số nguyên
    
    def get_current_node(self, agv_id_and_new_start, start):
        if(agv_id_and_new_start is None):
            return start
        if agv_id_and_new_start[0] == f'AGV{str(start)}':
            #print(agv_id_and_new_start[1])
            return agv_id_and_new_start[1]
        return start
    
    def getAllNewStartedNodes(self, excludedAgv = None):
        from .AGV import AGV
        allAGVs = AGV.allInstances()
        #pdb.set_trace()
        """for id in self.nodes:
            if self.nodes[id].agv is not None:
                if(excludedAgv is not None):
                    if(self.nodes[id].agv.id == excludedAgv.id):
                        continue
                if(len(allAGVs) == 0):
                    allAGVs.add(self.nodes[id].agv)
                elif any(agv.id == self.nodes[id].agv.id for agv in allAGVs):
                    allAGVs.add(self.nodes[id].agv)"""
        startedNodes = set()
        from .ReachingTargetEvent import ReachingTargetEvent
        for agv in allAGVs:
            if(not isinstance(agv.event, ReachingTargetEvent)):
                #if(len(agv.path) > 0):
                # #    startedNodes.append(agv.path[-1])
                startedNodes.add(agv.current_node)
        if(len(startedNodes) == 0):
            return self.graph_processor.startedNodes
        return startedNodes
        
    def write_to_file(self, agv_id_and_new_start = None, new_halting_edges = None, filename="TSG.txt"):
        #self.calling = self.calling + 1rite
        #print("Call write_to_file of Graph.py")
        #if(config.count == 2):
        #    pdb.set_trace()
        M = max(target.id for target in self.graph_processor.getTargets())
        m1 = max(edge[1] for edge in new_halting_edges)
        M = max(M, m1)
        num_halting_edges = len(new_halting_edges) if new_halting_edges is not None else 0
        #with open(filename, "w") as file:
        #    file.write(f"p min {len(self.nodes)} {len(self.adjacency_list)}\n")
        #    for node in self.nodes:
        #        file.write(f"n {node} 1\n")
        #    for start_node in self.adjacency_list:
        #        for end_node, weight in self.adjacency_list[start_node]:
        #            file.write(f"a {start_node} {end_node} 0 1 {weight}\n")
        Max = len(self.nodes)
        #pdb.set_trace()
        sorted_edges = sorted(self.adjacency_list.items(), key=lambda x: x[0])
        num_edges = self.count_edges()
        num_edges = num_edges + num_halting_edges
        
        with open(filename, 'w') as file:
            file.write(f"p min {M} {num_edges}\n")
            """if(Max == 8161 and num_edges == 13865):
                pdb.set_trace()
            for start in self.graph_processor.startedNodes:
                #pdb.set_trace()
                start_node = self.get_current_node(agv_id_and_new_start, start)
                #if(start_node == 24):
                #    pdb.set_trace()"""
            #if(self.calling == 6):
            #    pdb.set_trace()
            
            startedNodes = self.getAllNewStartedNodes()
            #buggySet1 = {43075, 42060}
            #buggySet2 = {41988, 42060}
            #if(startedNodes == buggySet1 or startedNodes == buggySet2):
            #    #print(f'Graph.py:566 {startedNodes}')
            #    pdb.set_trace()
            #if(len(startedNodes) != len(self.graph_processor.getTargets())):
            #    pdb.set_trace()
            for start_node in startedNodes:
                file.write(f"n {start_node} 1\n")
            for target in self.graph_processor.getTargets():
                target_id = target.id
                file.write(f"n {target_id} -1\n")
            #for edge in self.tsEdges:
            #for edge in self.ts_edges:
            new_nodes = set()
            for source_id, edges in sorted_edges:
                for edge in edges:
                    #if isinstance(edge[1], int):
                    #    pdb.set_trace()
                    t = edge[0] // self.graph_processor.M - (1 if edge[0] % self.graph_processor.M == 0 else 0)
                    """if(t > self.graph_processor.H):
                        if(isinstance(self.nodes[edge[0]], TimeoutNode) and edge[0] not in new_nodes):                            
                            #print(f'{self.nodes[edge[0]]} {edge[0] % self.graph_processor.M}')
                            new_nodes.add(edge[0])"""
                            #pdb.set_trace()
                    """if(edge[0] == 19685):
                        pdb.set_trace()"""
                    file.write(f"a {source_id} {edge[0]} {edge[1].lower} {edge[1].upper} {edge[1].weight}\n")  
            for edge in new_halting_edges:
                file.write(f"a {edge[0]} {edge[1]} {edge[2]} {edge[3]} {edge[4]}\n")
            #print("=================")
        """if(new_halting_edges is not None and self.continueDebugging):
            if(len(new_halting_edges) > 0):
                pdb.set_trace()
                continueDebugging = input("Bạn co muốn debug tiếp ở đây ko?: (Y/N)")
                if continueDebugging == "N":
                    self.continueDebugging = False"""
        
    """def update_edge(self, start_node, end_node, new_weight):
        found = False
        for i, (neighbor, weight) in enumerate(self.adjacency_list[start_node]):
            if neighbor == end_node:
                self.adjacency_list[start_node][i] = (end_node, new_weight)
                found = True
                break
        if found:
            print(f"Edge from {start_node} to {end_node} updated to new weight {new_weight}.")
        else:
            print(f"Edge from {start_node} to {end_node} not found to update.")"""

    def remove_node_and_origins(self, node_id):
        #pdb.set_trace()
        from .Node import Node
        #if(node_id == 51265):
        #    pdb.set_trace()
        node = None
        if isinstance(node_id, Node):
            node = node_id
        elif node_id in self.nodes:
            node = self.nodes[node_id]
        else:
            return
        node = node_id if isinstance(node_id, Node) else self.nodes[node_id]
        R = [node]  # Khởi tạo danh sách R với nút cần xóa
        while R:  # Tiếp tục cho đến khi R rỗng
            current_node = R.pop()  # Lấy ra nút cuối cùng từ R
            if current_node.id in self.nodes:  # Kiểm tra xem nút có tồn tại trong đồ thị hay không
                del self.nodes[current_node.id]  # Nếu có, xóa nút khỏi danh sách các nút
            for id in self.adjacency_list:
                edges = []
                found = False
                for end_id, edge in self.adjacency_list[id]:
                    if(end_id == node.id):
                        #del self.adjacency_list
                        found = True
                    else:
                        edges.append([end_id, edge])
                if(found):
                    self.adjacency_list[id] = edges
            #self.edges.pop(current_node, None)  # Xóa tất cả các cạnh liên kết với nút này
            #for edge_list in self.edges.values():  # Duyệt qua tất cả các cạnh còn lại trong đồ thị
            #    edge_list[:] = [(n, w) for n, w in edge_list if n != current_node]  # Loại bỏ nút khỏi danh sách các nút kết nối với mỗi cạnh
            # Thêm các nút chỉ được dẫn đến bởi nút hiện tại vào R
            #R.extend([n for n in self.edges if all(edge[0] == current_node for edge in self.edges[n])])

    def remove_edge(self, start_node, end_node, agv_id):
        if (start_node, end_node) in self.edges:
            del self.edges[(start_node, end_node)]
            self.lastChangedByAGV = agv_id  # Update the last modified by AGV

    def handle_edge_modifications(self, start_node, end_node, agv):
        # Example logic to adjust the weights of adjacent edges
        print(f"Handling modifications for edges connected to {start_node} and {end_node}.")
        #pdb.set_trace()
        adjacent_nodes_with_weights = self.adjacency_list.get(end_node, [])
        # Check adjacent nodes and update as necessary
        for adj_node, weight in adjacent_nodes_with_weights:
            if (end_node, adj_node) not in self.lastChangedByAGV or self.lastChangedByAGV[(end_node, adj_node)] != agv.id:
                # For example, increase weight by 10% as a traffic delay simulation
                new_weight = int(weight * 1.1)
                self.adjacency_list[end_node][adj_node] = new_weight
                print(f"Updated weight of edge {end_node} to {adj_node} to {new_weight} due to changes at {start_node}.")
    
    def __str__(self):
        return "\n".join(f"{start} -> {end} (Weight: {weight})" for start in self.adjacency_list for end, weight in self.adjacency_list[start])
    
#graph = Graph()

#def initialize_graph():
    # Function to populate the graph if needed
    #return graph
