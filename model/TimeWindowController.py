import os
import pdb
from collections import deque, defaultdict
from .utility import utility
import inspect
#from .RestrictionNode import RestrictionNode
from .TimeWindowNode import TimeWindowNode
from .TimeWindowEdge import TimeWindowEdge
from .Node import Node

class TimeWindowController:
    def __init__(self, alpha, beta, gamma):
        self.TWEdges = defaultdict(list)
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
    
    def add_source_and_TWNode(self, source_id, node, earliness, tardiness):
        #pdb.set_trace()
        if( isinstance(node, TimeWindowNode)):
            if(not source_id in self.TWEdges):
                self.TWEdges[source_id] = []
            found = False
            for old_node, _, _ in self.TWEdges[source_id]:
                if(old_node.id == node.id):
                    found = True
                    break
            if(not found):
                self.TWEdges[source_id].append([node, earliness, tardiness])

    def remove_source(self, source):
        if(source in self.TWEdges):
            del self.TWEdges[source]

    def generate_time_window_edges(self, node, adj_edges, M):
        space_id = (M if node.id % M == 0 else node.id % M)
        if(space_id in self.TWEdges):
            #nodes[node.id] = TimeWindowNode(node.id, "TimeWindow")
            for target_node, earliness, tardiness in self.TWEdges[space_id]:
                found = False
                if(node.id in adj_edges):
                    for end_id, edge in adj_edges[node.id]:
                        if(end_id == target_node.id and isinstance(edge, TimeWindowEdge)):
                            found = True
                if(not found):
                    if(not node.id in adj_edges):
                        adj_edges[node.id] = []
                    #target_node = self.TWEdges[space_id][0]
                    #earliness = self.TWEdges[space_id][1]
                    #tardiness = self.TWEdges[space_id][2]
                    i = node.id // M - (1 if node.id % M == 0 else 0)
                    C = int(int(self.beta) * max(earliness - i, 0, i - tardiness) / int(self.alpha))
                    edge = [node.id, target_node.id, 0, 1, C]
                    adj_edges[node.id].append((target_node.id, node.create_edge(target_node, M, -1, edge)))
