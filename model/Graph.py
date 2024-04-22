import AGV
import Edge
from collections import deque, defaultdict
from model.utility import utility
class Graph:
    def __init__(self):
        self.adjacency_list = defaultdict(list)
        self.nodes = set()
        self.lastChangedByAGV = -1
  
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
        with open("TSG.txt", "w") as file:
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
            
    def add_edge(self, start_node, end_node, weight, agv):
        if start_node not in self.adjacency_list:
            self.adjacency_list[start_node] = {}
        self.adjacency_list[start_node][end_node] = weight
        # Update the last AGV to change this edge
        self.lastChangedByAGV[(start_node, end_node)] = agv.id
        print(f"Edge added/updated from {start_node} to {end_node} with weight {weight} by AGV {agv.id}.")

    def get_edge(self, start_node, end_node):
        # Returns the edge if it exists
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

            
    def handle_edge_modifications(self, start_node, end_node, agv_id):
        # Implement custom logic for edge modifications
        self.lastChangedByAGV = agv_id  # Ensure every modification updates this
    
    def __str__(self):
        return "\n".join(f"{start} -> {end} (Weight: {edge.weight})" for (start, end), edge in self.edges.items())
