import os
import pdb
from collections import deque, defaultdict
from .utility import utility
import inspect
from .RestrictionNode import RestrictionNode
#from .TimeWindowNode import TimeWindowNode
#from .TimeWindowEdge import TimeWindowEdge
from .Node import Node

class RestrictionController:
    def __init__(self, alpha, beta, gamma, H, Ur, M):
        self.restrictionEdges = defaultdict(list)
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.H = H 
        self.Ur = Ur
        self.M = M
    
    def add_nodes_and_ReNode(self, end_at_aS, start_at_aT, restriction):
        #pdb.set_trace()
        #if( isinstance(node, RestrictionNode)):
        key = tuple(restriction)
        if(not key in self.restrictionEdges):
            self.restrictionEdges[key] = []
        found = False
        for to_aS, from_aT in self.restrictionEdges[key]:
            if(to_aS == end_at_aS and from_aT == start_at_aT):
                found = True
                break
        if(not found):
            self.restrictionEdges[key].append([end_at_aS, start_at_aT])

    def remove_restriction_edges(self, key):
        if(key in self.restrictionEdges):
            del self.restrictionEdges[key]

    def generate_restriction_edges(self, start_node, end_node, adj_edges, M):
        space_source = start_node.id % self.M if start_node.id % self.M != 0 else self.M
        space_destination = end_node.id % self.M if end_node.id % self.M != 0 else self.M
        #space_id = (M if node.id % M == 0 else node.id % M)
        key = tuple([space_source, space_destination])
        if(key in self.restrictionEdges):
            #nodes[node.id] = TimeWindowNode(node.id, "TimeWindow")
            found = False
            for to_aS, from_aT in self.restrictionEdges[key]:
                if(to_aS.start_node.id == start_node.id and from_aT.end_node == end_node.id):
                    found = True
                    break
            if(not found):
                if(not start_node.id in adj_edges):
                    adj_edges[start_node.id] = []
                #target_node = self.TWEdges[space_id][0]
                #earliness = self.TWEdges[space_id][1]
                #tardiness = self.TWEdges[space_id][2]
                i = start_node.id // M - (1 if start_node.id % M == 0 else 0)
                C = int(int(self.beta) * max(earliness - i, 0, i - tardiness) / int(self.alpha))
                edge = [node.id, target_node.id, 0, 1, C]
                adj_edges[node.id].append((target_node.id, node.create_edge(target_node, M, -1, edge)))