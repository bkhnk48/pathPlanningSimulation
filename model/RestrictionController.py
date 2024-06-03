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
    def __init__(self, alpha, beta, gamma, H, Ur, M, graph_processor):
        self.restrictionEdges = defaultdict(list)
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.H = H 
        self.Ur = Ur
        self.M = M
        self.graph_processor = graph_processor
    
    def add_nodes_and_ReNode(self, forward_to_aS, rise_from_aT, restriction):
        #pdb.set_trace()
        #if( isinstance(node, RestrictionNode)):
        key = tuple(restriction)
        if(not key in self.restrictionEdges):
            self.restrictionEdges[key] = []
        found = False
        for to_aS, from_aT in self.restrictionEdges[key]:
            if(to_aS == forward_to_aS and from_aT == rise_from_aT):
                found = True
                break
        if(not found):
            self.restrictionEdges[key].append([forward_to_aS, rise_from_aT])

    def remove_restriction_edges(self, key):
        if(key in self.restrictionEdges):
            del self.restrictionEdges[key]

    def generate_restriction_edges(self, start_node, end_node, adj_edges):
        space_source = start_node.id % self.M if start_node.id % self.M != 0 else self.M
        space_destination = end_node.id % self.M if end_node.id % self.M != 0 else self.M
        time_source = start_node.id // self.M - (1 if start_node.id % self.M == 0 else 0)
        time_destination = end_node.id // self.M - (1 if end_node.id % self.M == 0 else 0)
        #space_id = (M if node.id % M == 0 else node.id % M)
        key = tuple([space_source, space_destination])
        if(key in self.restrictionEdges):
            #nodes[node.id] = TimeWindowNode(node.id, "TimeWindow")
            found = False
            for to_aS, from_aT in self.restrictionEdges[key]:
                if(to_aS == start_node.id and from_aT == end_node.id):
                    found = True
                    break
            if(not found):
                self.restrictionEdges[key].append([start_node.id, end_node.id])
                if(not start_node.id in adj_edges):
                    adj_edges[start_node.id] = []
                #newA = set()
                e4 = (start_node.id, to_aS, 0, 1, 0)
                #cost = edges_with_cost.get((e[0], e[1]), -1)
                e5 = (from_aT, end_node.id, 0, 1, time_destination - time_source)
                #e5 = (aT, e[1], 0, 1, 1)
                #newA.update({e4, e5})
                pdb.set_trace()
                for e in [e4, e5]:
                    temp = self.graph_processor.find_node(e[0]).create_edge(self.graph_processor.find_node(e[1]), self.M, \
                                            self.graph_processor.d, e, True)
                    print("edge: ", temp)
                    adj_edges[e[0]].append([e[1], temp])
