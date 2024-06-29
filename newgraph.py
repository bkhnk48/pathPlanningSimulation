import os
import re
import json
from model.Edge import Edge
from model.Edge import HoldingEdge
from model.Edge import MovingEdge
from model.Edge import ArtificialEdge
from model.Edge import TimeWindowEdge
from model.Edge import RestrictionEdge
from model.ArtificialNode import ArtificialNode
from model.TimeWindowNode import TimeWindowNode
from model.RestrictionNode import RestrictionNode
from model.Node import Node
from collections import deque, defaultdict
from scipy.sparse import lil_matrix
from model.utility import utility
import newtestunit
import inspect

def get_space_id(id, max):
    if id % max != 0:
        return id % max
    else:
        return max
    
class Graph:
    def __init__(self):
        #self.adjacency_list = defaultdict(list)
        self.H = 0 
        self.M = 0
        self.d = 0
        self.nodes = {}
        self.alpha =  1
        self.beta =  1
        self.gamma =  1
        #self.lastChangedByAGV = -1
        self.edges = defaultdict(list)
        self.change_edges = defaultdict(list)
        self.list1 = [ ]
        self.neighbour_list = {}
        self.visited = set()
        self.id2_id4_list = []
        self.version = -1
        self.file_path = None
        self.cur = []
        self.map = {}
        self.numberOfNodesInSpaceGraph = -1
        self.earliness = 0
        self.tardiness = 0
        self.id = -1
        self.startedNodes = []
        self.targetNodes = []
        self.spaceEdges = defaultdict(list)
        self.reverse_Edges_id = defaultdict(list)
        print("Initialized a new graph.")
        stack = inspect.stack()
        for frame in stack[1:]:
            print(f"Hàm '{frame.function}' được gọi từ file '{frame.filename}' tại dòng {frame.lineno}")

    def add_restrictions(self):
        self.gamma = 1
        self.restriction_count = 1
        self.startBan = 0
        self.endBan = 2
        self.restrictions = [[2, 3]]
        self.Ur = 1
        self.startedNodes = [1, 10]
    
    def insertEdgesAndNodes(self, start, end, weight,lower=0,upper=1):
        if start not in self.edges:
            self.edges[start].append(Edge(start,end,lower,upper,weight))
            self.reverse_Edges_id[end].append(start)
        else:
            end_nodes = []
            for edge in self.edges[start]:
                end_nodes.append(edge.end_node)
            if end not in end_nodes:
                self.edges[start].append(Edge(start,end,lower,upper,weight))
                self.reverse_Edges_id[end].append(start)
        if start not in self.nodes:
            self.nodes[start] = Node(start)
        if end not in self.nodes:
            self.nodes[end] = Node(end)
            
    def inputfrommap(self,filepath):
        self.H = int(input("Nhap gia tri H:"))
        self.d = int(input("Nhap gia tri d:"))
        space_nodes = []
        largest_id = 0
        with open(filepath, 'r') as f:
            for line in f:
                part = line.split()
                if part[0] == 'a' and len(part) == 6:
                    id1,id2,weight = int(part[1]),int(part[2]),int(part[5])
                    self.spaceEdges[id1].append((id2,weight))
                    largest_id = max(largest_id, id1, id2)
                    if id1 not in space_nodes:
                        space_nodes.append(id1)
                    if id2 not in space_nodes:
                        space_nodes.append(id2)
        self.M = largest_id
        Q = deque()
        for node_id in space_nodes:
            Q.append(node_id)
        while Q:
            start_node = Q.popleft()
            for space_end_node,weight in self.spaceEdges[get_space_id(start_node,self.M)]:
                moving_node = (start_node//self.M - (1 if start_node % self.M == 0 else 0) + weight) *self.M + space_end_node
                if moving_node <=self.M*(self.H+1):
                    self.insertEdgesAndNodes(start_node,moving_node,weight)
                    Q.append(moving_node)
            holding_node = start_node + self.M*self.d
            if holding_node<=self.M*(self.H+1):
                self.insertEdgesAndNodes(start_node,holding_node,self.d)
                Q.append(holding_node)

    def count_edges(self):
        count = 0
        for node in self.edges:
            count += len(self.edges[node])
        return count
    
    def get_max_node_id(self):
        max_val = 0 
        for node_id in self.nodes:
            max_val = max(max_val,node_id)
        return max_val


    def create_tsg_file(self):
        with open('TSG.txt', 'w') as file:
            file.write(f"p min {self.get_max_node_id()} {self.count_edges()}\n")
            for start_node in self.startedNodes:
                file.write(f"n {start_node} 1\n")
            for end_node in self.targetNodes:
                file.write(f"n {end_node.id} -1\n")
            for start_node in self.edges:
                for edge in self.edges[start_node]:
                    file.write(f"a {edge.start_node} {edge.end_node} {edge.lower} {edge.upper} {edge.weight}\n")
    def getMaxID(self):
      max_val = 0
      try:
        with open('TSG.txt', 'r') as file:
            for line in file:
                parts = line.strip().split()
                if parts[0] == 'a':
                    max_val = max(max_val, int(parts[2]))
      except FileNotFoundError:
        pass
      return max_val
    
    def add_time_windows_constraints(self):
        max_val =  self.getMaxID()
        
        max_val = max_val + 1
        targetNode = TimeWindowNode(max_val, "TimeWindow",self.earliness,self.tardiness)
        self.nodes[max_val] = targetNode
        self.targetNodes.append(targetNode)
        for node in self.nodes:
            if get_space_id(node,self.M) == self.id:
                c = int(int(self.beta) * max(self.earliness - (int(node/(self.M)-1)), 0, (int(node/(self.M)-1)) - self.tardiness) / int(self.alpha))
                self.edges[node].append(TimeWindowEdge(node,max_val,0,1,c))
                with open('TSG.txt', 'a') as file:
                    file.write(f"a {node} {max_val} 0 1 {c}\n")



    def process_restrictions(self):
        self.Ban_edge = []
        for time in range(0,self.endBan+1):
            for restriction in self.restrictions:
                timeSpacePoint_0 = time*self.M + restriction[0]
                for edge in self.edges[timeSpacePoint_0]:
                    if get_space_id(edge.end_node,self.M) == restriction[1]:
                        if (edge.end_node//self.M - (1 if edge.end_node % self.M == 0 else 0)) >= self.startBan:
                            self.Ban_edge.append((timeSpacePoint_0,edge.end_node))
                self.edges[timeSpacePoint_0] = [ edge for edge in self.edges[timeSpacePoint_0]
                                                         if get_space_id(edge.end_node, self.M) != restriction[1]]


        if self.Ban_edge:
            max = self.getMaxID()  + 1
            aS, aT, aSubT = max, max + 1, max + 2
            self.nodes[aS] = RestrictionNode(aS)
            self.nodes[aT] = RestrictionNode(aT)
            self.nodes[aSubT] = RestrictionNode(aSubT)
            self.edges[aS].append(RestrictionEdge(aS,aT,0, self.H,int(self.gamma/self.alpha)))
            self.edges[aS].append(RestrictionEdge(aS,aSubT,0, self.Ur,0))
            self.edges[aSubT].append(RestrictionEdge(aSubT,aT,0,self.H, 0))
            for pair_node in self.Ban_edge:
                self.edges[pair_node[0]].append(RestrictionEdge(pair_node[0],aS,0,1,0))
                weight = int((pair_node[1]-get_space_id(pair_node[1],self.M))/self.M)-int((pair_node[0]-get_space_id(pair_node[0],self.M))/self.M)
                self.reverse_Edges_id[pair_node[1]].remove(pair_node[0])
                self.edges[aT].append(RestrictionEdge(aT,pair_node[1],0,1,weight))
            self.create_tsg_file()
    
    def node_still_exists(self,node_id,pre_node_id):
        past_nodes = []
        if pre_node_id in self.reverse_Edges_id[node_id]:
            self.reverse_Edges_id[node_id].remove(pre_node_id)
        if len(self.reverse_Edges_id[node_id]) == 0 and node_id not in self.spaceEdges :
            return False
        else:
            return True
    
    def update_TimeWindowEdges(self):
        res_nodes = [self.nodes[node_id] for node_id in self.nodes if isinstance(self.nodes[node_id],TimeWindowNode)]
        for node_id in self.nodes:
            if not isinstance(self.nodes[node_id],(TimeWindowNode,RestrictionNode)) and get_space_id(node_id,self.M) == self.id:
                pair_node = [(node_id,edge.end_node) for edge in self.edges[node_id]]
                for res_node in res_nodes:
                    c = int(int(self.beta) * max(res_node.earliness - (int(node_id/(self.M)-1)), 0, (int(node_id/(self.M)-1)) - res_node.tardiness) / int(self.alpha))
                    if (node_id,res_node.id) not in pair_node:
                        self.edges[node_id].append(TimeWindowEdge(node_id,res_node.id,0,1,c))
    
    def update_Restriction(self):
        max_val = self.get_max_node_id()
        aT = max_val - 1
        aS = max_val - 2
        end_node_id_and_weight = []
        for edges_id in self.Ban_edge:
            if edges_id[0] not in self.edges:
                self.Ban_edge.remove(edges_id)
            else:
                weight = (edges_id[1]//self.M - (1 if edges_id[1] % self.M == 0 else 0) )  - (edges_id[0]//self.M  - (1 if edges_id[0] % self.M == 0 else 0))
                end_node_id_and_weight.append((edges_id[1],weight))
        
        for edge in self.edges[aT]:
            if (edge.end_node,edge.weight) not in end_node_id_and_weight:
                self.edges[aT].remove(edge)
        
        for time in range(0,self.endBan+1):
            for restriction in self.restrictions:
                timeSpacePoint_0 = time*self.M + restriction[0]
                for edge in self.edges[timeSpacePoint_0]:
                    if get_space_id(edge.end_node,self.M) == restriction[1] and not isinstance(self.nodes[edge.end_node],(TimeWindowNode,RestrictionNode)):
                        if (edge.end_node//self.M - (1 if edge.end_node % self.M == 0 else 0)) >= self.startBan:
                            self.Ban_edge.append((timeSpacePoint_0,edge.end_node))
        
        for pair_node in self.Ban_edge:
            edges_id = [edge.end_node for edge in self.edges[pair_node[0]] ]
            if aS not in edges_id:
                self.edges[pair_node[0]].append(RestrictionEdge(pair_node[0],aS,0,1,0))
                weight = int((pair_node[1]-get_space_id(pair_node[1],self.M))/self.M)-int((pair_node[0]-get_space_id(pair_node[0],self.M))/self.M)
                aT_end_nodes_id = [edge.end_node for edge in self.edges[aT]]
                if pair_node[1] not in aT_end_nodes_id:
                    self.edges[aT].append(RestrictionEdge(aT,pair_node[1],0,1,weight))
               

    def update_graph(self,id1, id2, c12):
        i1, i2 = id1 // self.M, id2 // self.M-(1 if  id2 % self.M == 0 else 0)
        if i2 - i1 != c12:
            print('Status: i2 - i1 != C12')
            newid2 = (i1 + c12)*self.M + get_space_id(id2,self.M)
            self.insertEdgesAndNodes(id1,newid2,c12)
            
            Q = deque()
            Q.append((id1,id2))
            while Q:
                nodes_id = Q.popleft()
                if nodes_id[0] in self.edges:
                    self.edges[nodes_id[0]] = {edge for edge in self.edges[nodes_id[0]] 
                                                    if edge.end_node != nodes_id[1]}

                if not self.node_still_exists(nodes_id[1],nodes_id[0]):

                    for edge in self.edges[nodes_id[1]]:
                        end_node = edge.end_node
                        if not isinstance(self.nodes[end_node], (TimeWindowNode, RestrictionNode)):
                                Q.append((nodes_id[1],end_node))
                        
                    del self.edges[nodes_id[1]]
                    del self.nodes[nodes_id[1]]
            
            Q1 = deque()
            Q1.append(newid2)
            while Q1:
                node_id = Q1.popleft()
                egdes_id = [edge.end_node for edge in self.edges[node_id]]
                for end_node,weight in self.spaceEdges[get_space_id(node_id,self.M)]:
                    new_target_id = (node_id//self.M - (1 if node_id % self.M == 0 else 0) + weight)*self.M + end_node
                    if new_target_id not in egdes_id:
                        if new_target_id <= self.M*(self.H+1):
                            self.insertEdgesAndNodes(node_id,new_target_id,weight)
                            Q1.append(new_target_id)
                        
                hodling_node = node_id + self.M*self.d
                if hodling_node not in egdes_id:
                    if new_target_id <= self.M*(self.H+1):
                        self.insertEdgesAndNodes(node_id,hodling_node,self.d)
                        Q1.append(hodling_node) 


            self.update_TimeWindowEdges()
            self.update_Restriction()
            self.create_tsg_file()
                

if __name__ == "__main__":    
    graph = Graph()
    graph.inputfrommap("2ndSimple.txt")
    graph.create_tsg_file()
    newtestunit.assert_Nodes_and_Edges(graph)
    #assert_Nodes_and_Edges(graph)
    count = 0
    
    while(count <= 1):
        graph.id = 3
        graph.earliness = 4 if count == 0 else 7
        graph.tardiness = 6 if count == 0 else 9
        graph.alpha = 1
        graph.beta = 1
        graph.add_time_windows_constraints()
        count += 1
    graph.add_restrictions()
    graph.process_restrictions()
    graph.update_graph(1,8,3)
    graph.update_graph(2,8,1)
    newtestunit.assert_TimeWindowNodes(graph)
    newtestunit.assert_Restriction(graph)
    #assert_Nodes(graph,3)
#def initialize_graph():
    # Function to populate the graph if needed
    #return graph