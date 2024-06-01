import os
import pdb
from collections import deque, defaultdict
from .utility import utility
import inspect
#from .RestrictionNode import RestrictionNode
from .TimeWindowNode import TimeWindowNode
from .Node import Node

class TimeWindowController:
    def __init__(self):
        self.TWEdges = defaultdict(list)
    
    def add_source_and_TWNode(self, source, node):
        if( isinstance(node, TimeWindowNode)):
            if(not source in self.TWEdges):
                self.TWEdges[source] = node

    def remove_source(self, source):
        if(source in self.TWEdges):
            del self.TWEdges[source]

    def generate_edges(self, node, nodes, adj_edges, M):
        space_id = node.id // M - (1 if node.id % M == 0 else 0)
        if(space_id in self.TWEdges and not isinstance(node, TimeWindowNode)):
            nodes[node.id] = TimeWindowNode(node.id, "TimeWindow")


