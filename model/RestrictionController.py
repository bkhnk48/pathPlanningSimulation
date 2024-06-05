import os
import pdb
from collections import deque, defaultdict
from .utility import utility
import inspect
from .RestrictionNode import RestrictionNode
from .TimeWindowNode import TimeWindowNode
#from .TimeWindowEdge import TimeWindowEdge
from .Node import Node

class RestrictionController:
    def __init__(self, graph_processor):
        self.restrictionEdges = defaultdict(list)
        self.alpha = graph_processor.alpha
        self.beta = graph_processor.beta
        self.gamma = graph_processor.gamma
        self.H = graph_processor.H 
        self.Ur = graph_processor.Ur
        self.M = graph_processor.M
        self.graph_processor = graph_processor
    
    def add_nodes_and_ReNode(self, forward_to_aS, rise_from_aT, restriction, aS, aT):
        #pdb.set_trace()
        #if( isinstance(node, RestrictionNode)):
        key = tuple(restriction)
        if(not key in self.restrictionEdges):
            self.restrictionEdges[key] = []
        found = False
        for to_aS, from_aT, _, _ in self.restrictionEdges[key]:
            if(to_aS == forward_to_aS and from_aT == rise_from_aT):
                found = True
                break
        if(not found):
            self.restrictionEdges[key].append([forward_to_aS, rise_from_aT, aS, aT])

    def remove_restriction_edges(self, key):
        if(key in self.restrictionEdges):
            del self.restrictionEdges[key]

    """def find_aS_and_aT(self, source_id, target_id, nodes, adj_edges, debug = False):
        aS = None
        if(debug):
            pdb.set_trace()
        space_id = source_id % self.M if source_id % self.M != 0 else self.M
        for id in nodes:
            if(id == 5):
                pdb.set_trace()
            s_id = id % self.M if id % self.M != 0 else self.M
            if(s_id == space_id and (not isinstance(nodes[id], RestrictionNode))):
                for end_id, edge in adj_edges[id]:
                    if isinstance(nodes[end_id], RestrictionNode):
                        aS = nodes[end_id]
                        break
            if (aS != None):
                break
        assert (aS != None)
        aT = None
        is_aT = True
        if(debug):
            pdb.set_trace()
        for end_id, edge in adj_edges[aS.id]:
            if (edge.upper == self.H and edge.weight == int(self.gamma/self.alpha)):
                is_aT = True
                for node_id, e in adj_edges[end_id]:
                    if isinstance(e.end_node, RestrictionNode):
                        is_aT = False
                        break
                    elif node_id == target_id:
                        break
                if(is_aT):
                    aT = self.graph_processor.nodes[end_id]
                    break
        return [aS, aT]"""



    def generate_restriction_edges(self, start_node, end_node, nodes, adj_edges):
        space_source = start_node.id % self.M if start_node.id % self.M != 0 else self.M
        space_destination = end_node.id % self.M if end_node.id % self.M != 0 else self.M
        time_source = start_node.id // self.M - (1 if start_node.id % self.M == 0 else 0)
        time_destination = end_node.id // self.M - (1 if end_node.id % self.M == 0 else 0)
        if(not (time_source >= self.graph_processor.endBan or time_destination <= self.graph_processor.startBan)):
        #space_id = (M if node.id % M == 0 else node.id % M)
            pdb.set_trace()
            key = tuple([space_source, space_destination])
            if(key in self.restrictionEdges):
                #nodes[node.id] = TimeWindowNode(node.id, "TimeWindow")
                found = False
                for element in self.restrictionEdges[key]:
                    if(element[0] == start_node.id and element[1] == end_node.id):
                        aS = element[2]
                        aT = element[3]
                        found = True
                        break
                if(found):
                    #self.restrictionEdges[key].append([start_node.id, end_node.id, aS, aT])
                    #if(not start_node.id in adj_edges):
                    #    adj_edges[start_node.id] = []
                    #newA = set()
                    
                    """e4 = (start_node.id, to_aS, 0, 1, 0)
                    #cost = edges_with_cost.get((e[0], e[1]), -1)
                    e5 = (from_aT, end_node.id, 0, 1, time_destination - time_source)
                    #e5 = (aT, e[1], 0, 1, 1)
                    #newA.update({e4, e5})
                    pdb.set_trace()
                    for e in [e4, e5]:
                        sourceNode = self.graph_processor.find_node(e[0])
    
                        destNode = self.graph_processor.find_node(e[1])
                        temp = sourceNode.create_edge(destNode, self.M, \
                                                self.graph_processor.d, e, True)
                        print("edge: ", temp)
                        adj_edges[e[0]].append([e[1], temp])"""
                    #[aS, aT] = self.find_aS_and_aT(start_node.id, end_node.id, nodes, adj_edges, True)
                    #pdb.set_trace()
                    e1 = (start_node.id, aS, 0, 1, 0)
                    temp1 = start_node.create_edge(self.graph_processor.find_node[aS], self.M, self.graph_processor.d, e1)
                    print("edge: ", temp1, end = '')
                    adj_edges[start_node.id].append([aS, temp1])
                    e2 = (end_node.id, aT, 0, 1, time_destination - time_source)
                    temp2 = self.graph_processor.find_node(aT).create_edge(end_node, self.M, self.graph_processor.d, e2)
                    adj_edges[aT].append(end_node.id, temp2)
