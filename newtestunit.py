from model.Graph import Graph#, graph
from model.AGV import AGV
from model.Event import Event, debug
from model.StartEvent import StartEvent
from model.Graph import Graph
from model.TimeWindowNode import TimeWindowNode
from model.RestrictionNode import RestrictionNode 
from model.Edge import TimeWindowEdge
from model.Edge import RestrictionEdge
import config
#from discrevpy import simulator
import newgraph
from newgraph import get_space_id 
import subprocess
import sys
import pdb

def assert_Nodes_and_Edges(graph):
    # Construct a list of space edges with weights
    space_edges = []
    for start_node_id, edges in graph.spaceEdges.items():
        for end_node_id, weight in edges:
            space_edges.append((start_node_id, end_node_id, weight))

    # Convert space_edges to a set for O(1) average time complexity in lookups
    space_edges_set = set(space_edges)
    
    # Validate the edges in the graph
    for edge_id, edges in graph.edges.items():
        for edge in edges:
            # Skip edges of type TimeWindowEdge or RestrictionEdge
            if isinstance(edge, (TimeWindowEdge, RestrictionEdge)):
                continue
            
            start_space_id = get_space_id(edge.start_node, graph.M)
            end_space_id = get_space_id(edge.end_node, graph.M)
            
            if start_space_id == end_space_id:
                # Ensure that the difference between end_node and start_node equals M * d
                assert edge.end_node - edge.start_node == graph.M * graph.d, \
                    f"Assertion failed as edge {edge} which satisfies conditions"
            else:
                # Calculate the weight and validate its existence in space_edges
                weight = int(((edge.end_node - end_space_id) - (edge.start_node - start_space_id)) / graph.M)
                assert (start_space_id, end_space_id, weight) in space_edges_set and edge.end_node <= graph.M *(graph.H+1), \
                    f"Assertion failed as edge {edge} which satisfies conditions"


def assert_TimeWindowNodes(graph):
    totalcount = 0
    start_node_connections = 0
    TWnodes = 0
    for edge_id in graph.edges:
        if get_space_id(edge_id,graph.M) == graph.id and not isinstance(graph.nodes[edge_id],(TimeWindowNode,RestrictionNode)):
            count = 0
            for edge in graph.edges[edge_id]:
                if isinstance(edge,TimeWindowEdge):
                    count += 1
            assert(count > 0),f"TimeWindowNode with id {edge.start_node,edge.end_node} has no incoming edges"
            totalcount = totalcount + count
    for node_id in graph.nodes:
        if get_space_id(node_id,graph.M) == graph.id and not isinstance(graph.nodes[node_id],(TimeWindowNode,RestrictionNode)):
            start_node_connections += 1
        if isinstance(graph.nodes[node_id],TimeWindowNode):
            TWnodes += 1
    assert(totalcount == TWnodes*start_node_connections),f"Number of new TimeWindowEdges does not meet the constraint"

def assert_Restriction(graph):
    aSubT = graph.getMaxID()
    aT = aSubT - 1
    aS = aT - 1
    count = 0
    for node_id in graph.nodes:
        if not isinstance(graph.nodes[node_id],(TimeWindowNode,RestrictionNode)):
            for edge in graph.edges[node_id]:
                if isinstance(edge,RestrictionEdge):
                    count += 1
    
    assert(len(graph.edges[aT])  == count),f"Number of new RestrictionEdges with non-RestrictionNode end nodes does not meet the constraint"