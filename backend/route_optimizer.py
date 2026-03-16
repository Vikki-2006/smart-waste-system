import networkx as nx

# Mock distances between locations for Dijkstra's algorithm
# Locations are mapped to bin_ids 1 to 10
edges = [
    (1, 2, 5), (1, 3, 8), (2, 4, 3), (3, 4, 4),
    (4, 5, 2), (5, 6, 6), (3, 7, 7), (7, 8, 3),
    (6, 9, 4), (8, 10, 5), (9, 10, 6), (2, 7, 10)
]

def build_graph():
    G = nx.Graph()
    G.add_weighted_edges_from(edges)
    return G

def optimize_route(bins_to_collect, start_node=1):
    """
    Finds a naive route to visit all bins_to_collect starting from start_node.
    Uses Dijkstra to find shortest paths between consecutive nodes to visit.
    For a real TSP (Traveling Salesperson Problem), OR-Tools would be better.
    This is a simplified greedy approach for demonstration.
    """
    if not bins_to_collect:
        return {"route": [], "total_distance": 0}
        
    G = build_graph()
    
    # Simple greedy TSP: from current node, go to the nearest unvisited required node
    current_node = start_node
    unvisited = set([b['id'] for b in bins_to_collect])
    
    route = [current_node]
    total_distance = 0
    
    while unvisited:
        # Find shortest path from current_node to all unvisited
        shortest_paths = nx.single_source_dijkstra_path_length(G, current_node)
        
        # Filter to unvisited nodes and find the closest
        reachable_unvisited = {node: dist for node, dist in shortest_paths.items() if node in unvisited}
        
        if not reachable_unvisited:
            break # Disconnected graph, shouldn't happen with our mock data unless a node is truly isolated
            
        next_node = min(reachable_unvisited, key=reachable_unvisited.get)
        distance = reachable_unvisited[next_node]
        
        # We don't trace the full path here, just the points we stop at
        route.append(next_node)
        total_distance += distance
        unvisited.remove(next_node)
        current_node = next_node
        
    # Return to depot (start_node)
    try:
        dist_to_start = nx.dijkstra_path_length(G, current_node, start_node)
        route.append(start_node)
        total_distance += dist_to_start
    except nx.NetworkXNoPath:
        pass
        
    return {"route": route, "total_distance": total_distance}
