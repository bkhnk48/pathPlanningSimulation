from collections import deque, defaultdict
from .utility import utility
import os
import pdb
class Graph:
    def __init__(self):
        self.adjacency_list = defaultdict(list)
        self.nodes = set()
        #self.lastChangedByAGV = -1
        self.edges = {}
        self.list1 = [ ]
        self.neighbour_list = {}
        self.visited = set()
        self.id2_id4_list = []
        self.version = -1
        self.file_path = None
        self.cur = []
        self.map = {}
        self.numberOfNodesInSpaceGraph = -1
        
    def insertEdgesAndNodes(self, start, end, weight):
        if start not in self.edges:
            self.edges[start] = []
        self.edges[start].append((end, weight))
    
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

    def writefile(self,startpos,inAGV):
        with open("TSG_0.txt", "w") as file:
            size = len(self.matrix)
            file.write("p min 82800 "+str(size)+"\n")
            file.write("n "+str(startpos)+" "+str(inAGV)+"\n")
            file.write("n "+str(82800)+str(0-inAGV)+"\n")
            for (i,j) in self.matrix:
                file.write("a "+str(i)+" "+str(j)+" 0 1 "+str(self.matrix[i, j]) + "\n")
                
    def add_node(self, node, properties=None):
        if properties is None:
            properties = {}
        self.nodes[node] = properties

    def update_node(self, node, **properties):
        if node in self.nodes:
            self.nodes[node].update(properties)
        else:
            self.nodes[node] = properties
            
    def add_edge(self, start_node, end_node, weight):
        if start_node not in self.adjacency_list:
            self.adjacency_list[start_node] = {}
        self.adjacency_list[start_node][end_node] = weight

    def get_edge(self, start_node, end_node):
        return self.adjacency_list.get(start_node, {}).get(end_node, None)
    
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
    
    def update_graph(self, currentpos, nextpos, realtime):
        # Update the graph with new edge information
        self.add_edge(currentpos, nextpos, realtime)
        
    def write_to_file(self, filename="TSG.txt"):
        with open(filename, "w") as file:
            file.write(f"p min {len(self.nodes)} {len(self.adjacency_list)}\n")
            for node in self.nodes:
                file.write(f"n {node} 1\n")
            for start_node in self.adjacency_list:
                for end_node, weight in self.adjacency_list[start_node]:
                    file.write(f"a {start_node} {end_node} 0 1 {weight}\n")
                    
    def update_edge(self, start_node, end_node, new_weight, agv):
        if start_node in self.adjacency_list and end_node in self.adjacency_list[start_node]:
            self.adjacency_list[start_node][end_node] = new_weight
            # Update the last AGV to change this edge
            self.lastChangedByAGV[(start_node, end_node)] = agv.id
            print(f"Edge weight from {start_node} to {end_node} updated to {new_weight} by AGV {agv.id}.")
        else:
            print("Edge does not exist to update.")

    def remove_node(self, node):
        if node in self.nodes:
            del self.nodes[node]
            self.edges.pop(node, None)
            for edges in self.edges.values():
                edges[:] = [(n, w) for n, w in edges if n != node]

    def remove_edge(self, start_node, end_node, agv_id):
        if (start_node, end_node) in self.edges:
            del self.edges[(start_node, end_node)]
            self.lastChangedByAGV = agv_id  # Update the last modified by AGV

    def handle_edge_modifications(self, start_node, end_node, agv):
        # Example logic to adjust the weights of adjacent edges
        print(f"Handling modifications for edges connected to {start_node} and {end_node}.")
        # Check adjacent nodes and update as necessary
        for adj_node, weight in self.adjacency_list.get(end_node, {}).items():
            if (end_node, adj_node) not in self.lastChangedByAGV or self.lastChangedByAGV[(end_node, adj_node)] != agv.id:
                # For example, increase weight by 10% as a traffic delay simulation
                new_weight = int(weight * 1.1)
                self.adjacency_list[end_node][adj_node] = new_weight
                print(f"Updated weight of edge {end_node} to {adj_node} to {new_weight} due to changes at {start_node}.")
    
    def __str__(self):
        return "\n".join(f"{start} -> {end} (Weight: {edge.weight})" for (start, end), edge in self.edges.items())
    
    def find_unique_numbers(self):
        if not os.path.exists(self.file_path):
            print(f"File {self.file_path} does not exist.")
            return []
    
        unique_numbers = set()
        id3_numbers = set()

        with open(self.file_path, 'r') as file:
            lines = file.readlines()

            for line in lines:
                if line.startswith('a'):
                    numbers = line.split()
                    id3 = int(numbers[3])
                    id3_numbers.add(id3)

            for line in lines:
                if line.startswith('a'):
                    numbers = line.split()
                    id1 = int(numbers[1])
                    if id1 not in id3_numbers:
                        unique_numbers.add(id1)
    
        return unique_numbers
    
    def create_trees(self):
        #self.list1 = []
        #self.neighbour_list = {}
        id1_id3_tree = defaultdict(list)
        pdb.set_trace()

        with open(self.file_path, 'r') as file:
            lines = file.readlines()
        #print(lines)
        for line in lines:
            if line.startswith('a'):
                #print(line)
                numbers = line.split()
                id1 = int(numbers[1])
                id3 = int(numbers[2])
                id2 = id1 % self.numberOfNodesInSpaceGraph
                id4 = id3 % self.numberOfNodesInSpaceGraph
                self.neighbour_list[id1] = id2
                self.neighbour_list[id3] = id4
                self.list1.append(id1)
                id1_id3_tree[id1].append(id3)
                id1_id3_tree[id3].append(id1)
    
        return id1_id3_tree

    def dfs(self, tree, start_node):
        self.visited.add(start_node)
        for node in tree[start_node]:
            if node not in self.visited:
                #print(node, end=' ')
                self.cur.append(node)
                self.id2_id4_list.append(self.neighbour_list[node])
                self.dfs(tree, node)
                
    def setTrace(self, file_path):
        self.file_path = file_path #'traces.txt'
        self.list1 = []
        self.neighbour_list = {}
        self.visited = set()
        self.id2_id4_list = []
        self.map = {}
        #pdb.set_trace()
        unique_numbers = self.find_unique_numbers()
        #print(unique_numbers)
        id1_id3_tree = self.create_trees()
        for number in self.list1:
            if not number in self.visited:
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
    
graph = Graph()

def initialize_graph():
    # Function to populate the graph if needed
    return graph
