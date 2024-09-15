import heapq

def read_input(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    start_points = []
    end_points = []
    edges = []
    
    for line in lines:
        parts = line.strip().split()
        if parts[0] == 'n' and parts[-1] == '1':
            start_points.append(' '.join(parts[1:-1]))
        elif parts[0] == 'n' and parts[-1] == '-1':
            end_points.append(' '.join(parts[1:-1]))
        elif parts[0] == 'a':
            edges.append((parts[1], parts[2], int(parts[3])))
    
    return start_points, end_points, edges

def dijkstra(graph, start):
    queue = [(0, start)]
    distances = {start: 0}
    while queue:
        current_distance, current_node = heapq.heappop(queue)
        if current_distance > distances[current_node]:
            continue
        for neighbor, weight in graph[current_node]:
            distance = current_distance + weight
            if neighbor not in distances or distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(queue, (distance, neighbor))
    return distances

def find_shortest_paths(start_points, end_points, edges):
    graph = {}
    for edge in edges:
        source, destination, weight = edge
        if source not in graph:
            graph[source] = []
        graph[source].append((destination, weight))
    
    results = {}
    for start in start_points:
        distances = dijkstra(graph, start)
        results[start] = {end: distances.get(end, float('inf')) for end in end_points}
    
    return results

def main(file_path):
    start_points, end_points, edges = read_input(file_path)
    results = find_shortest_paths(start_points, end_points, edges)
    
    for start in results:
        print(f"Start point: {start}")
        for end in results[start]:
            print(f"  End point: {end}, Shortest path length: {results[start][end]}")

# Example usage
file_path = "TSG.txt"
main(file_path)