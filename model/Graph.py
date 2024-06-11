import os
import pdb
from collections import deque, defaultdict
from .utility import utility
import inspect
from .RestrictionNode import RestrictionNode
from .TimeWindowNode import TimeWindowNode

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
        self.id2_id4_list = []
        self.version = -1
        self.file_path = None
        self.cur = []
        self.map = {}
        self.numberOfNodesInSpaceGraph = -1 if graph_processor is None else graph_processor.M
        #print("Initialized a new graph.")
        #stack = inspect.stack()
        #for frame in stack[1:]:
        #    print(f"Hàm '{frame.function}' được gọi từ file '{frame.filename}' tại dòng {frame.lineno}")
        
    
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
    
    def build_path_tree(self, file_path = 'traces.txt'):
        """ Build a tree from edges listed in a file for path finding. """
        id1_id3_tree = defaultdict(list)
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line.startswith('a'):
                    numbers = line.split()
                    id1 = int(numbers[1])
                    id3 = int(numbers[2])
                    id2 = id1 % self.numberOfNodesInSpaceGraph
                    id4 = id3 % self.numberOfNodesInSpaceGraph
                    node1 = self.nodes[id1]
                    #node2 = self.nodes[id2]
                    node3 = self.nodes[id3]
                    #node4 = self.nodes[id4]
                    #self.insertEdgesAndNodes(node1, node3, node2)
                    #self.insertEdgesAndNodes(node3, node1, node4)
                    self.neighbour_list[id1] = id2
                    self.neighbour_list[id3] = id4
                    #print(self.graph_processor.startedNodes)
                    #pdb.set_trace()
                    if(id1 in self.graph_processor.startedNodes):
                        self.list1.append(id1)
                    id1_id3_tree[id1].append(node3)
                    id1_id3_tree[id3].append(node1)
        return id1_id3_tree

    def dfs(self, tree, start_node):
        self.visited.add(start_node)
        for node in tree[start_node]:
            node_id = node if isinstance(node, int) else node.id
            if node_id not in self.visited:
                #print(node, end=' ')
                self.cur.append(node)
                self.id2_id4_list.append(self.neighbour_list[node_id])
                self.dfs(tree, node_id)

    def setTrace(self, file_path = 'traces.txt'):
        #pdb.set_trace()
        self.file_path = file_path #'traces.txt'
        self.list1 = []
        self.neighbour_list = {}
        self.visited = set()
        self.id2_id4_list = []
        self.map = {}
        #pdb.set_trace()
        #unique_numbers = self.find_unique_numbers()
        unique_numbers = self.find_unique_nodes()
        #print(unique_numbers)
        #id1_id3_tree = self.create_trees()
        id1_id3_tree = self.build_path_tree()
        for number in self.list1:
            if number not in self.visited:
                #print(number, end=' ')
                self.id2_id4_list.append(self.neighbour_list[number])
                self.cur = []
                self.dfs(id1_id3_tree, number)
                self.map[number] = self.cur
                #print('#', end=' ')
                #print(' '.join(map(str, id2_id4_list)))
                self.id2_id4_list = []
    
    def getTrace(self, idOfAGV):
        #pdb.set_trace()
        idOfAGV = int(idOfAGV[3:])
        for key, value in self.map.items():
            print(f"Key: {key}, Value: {value}")
        return self.map[idOfAGV]     
    
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
        if node in self.nodes:
            self.nodes[node].update(properties)
            print(f"Node {node} updated with properties {properties}.")
        else:
            self.nodes[node] = properties
            print(f"Node {node} added with properties {properties}.")
 
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
    
    def update_graph(self, id1 = -1, id2 = -1, c12 = -1):
    #ý nghĩa của các tham số: id1 - id của nút nguồn X trong đồ thị TSG
    #                         id2 - id cuả nút đích dự kiến Y trong đồ thị TSG
    #                         c12 - thời gian thực tế mà AGV di chuyển từ nút X đến Y
        # Update the graph with new edge information
        #self.add_edge(currentpos, nextpos, realtime)
        ID1 = int(input("Nhap ID1: ")) if id1 == -1 else id1
        ID2 = int(input("Nhap ID2: ")) if id2 == -1 else id2
        C12 = int(input("Nhap trong so C12: ")) if c12 == -1 else c12
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
        current_time = time1 + C12 # Giá trị của current_time
        #if(current_time > self.graph_processor.H):
        #    pdb.set_trace()
        current_time = current_time if current_time <= self.graph_processor.H else self.graph_processor.H
        new_node_id = current_time*M + (ID2 % M)
        #if(new_node_id == 45):
        #    pdb.set_trace()
            
        # Duyệt qua từng phần tử của adjacency_list
        for source_id, edges in list(self.adjacency_list.items()):
            # Tính giá trị time
            node = self.nodes[source_id]
            time = source_id // M - (1 if source_id % M == 0 else 0)
            # Nếu time < current_time, not isinstance(node, (TimeWindowNode, RestrictionNode))
            if time < current_time and not isinstance(node, (TimeWindowNode, RestrictionNode)):
                del self.adjacency_list[source_id]
                del self.nodes[source_id]
        
        Q = deque()
        Q.append(new_node_id)
        #pdb.set_trace()
        new_edges = self.graph_processor.insert_from_queue(Q)
        #print(new_edges)
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
        self.write_to_file()
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

    def parse_string(self, input_string):
        parts = input_string.split()
        if len(parts) != 6 or parts[0] != "a":
            return None  # Chuỗi không đúng định dạng
        try:
            ID1, ID2, L, U, C = map(int, parts[1:])
            return [ID1, ID2, L, U, C]
        except ValueError:
            return None  # Không thể chuyển thành số nguyên

        
    def write_to_file(self, filename="TSG.txt"):
        #with open(filename, "w") as file:
        #    file.write(f"p min {len(self.nodes)} {len(self.adjacency_list)}\n")
        #    for node in self.nodes:
        #        file.write(f"n {node} 1\n")
        #    for start_node in self.adjacency_list:
        #        for end_node, weight in self.adjacency_list[start_node]:
        #            file.write(f"a {start_node} {end_node} 0 1 {weight}\n")
        Max = len(self.nodes)
        num_edges = self.count_edges()
        sorted_edges = sorted(self.adjacency_list.items(), key=lambda x: x[0])
        with open(filename, 'w') as file:
            file.write(f"p min {Max} {num_edges}\n")
            for start in self.graph_processor.startedNodes:
                file.write(f"n {start} 1\n")
            for target in self.graph_processor.targetNodes:
                target_id = target.id
                file.write(f"n {target_id} -1\n")
            #for edge in self.tsEdges:
            #for edge in self.ts_edges:
            for source_id, edges in sorted_edges:
                for edge in edges:
                    if isinstance(edge[1], int):
                        pdb.set_trace()
                    file.write(f"a {source_id} {edge[0]} {edge[1].lower} {edge[1].upper} {edge[1].weight}\n")        
        
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
