import json
import numpy as np


def read_json(file_path: str) -> str:
    with open(file_path, 'r') as json_file:
        data = json_file.read()
    return data

def extract_all_objects(rankings: list[list[int, list[int]]]) -> set:
    all_objects = set()
    for ranking in rankings:
        for cluster in ranking:
            if not isinstance(cluster, list):
                cluster = [cluster]
            all_objects.update(cluster)
    return all_objects


def find_contradiction_kernel(matrix_ab: np.ndarray, matrix_ab_prime: np.ndarray) -> list[list[int]]:
    kernel = []
    n = matrix_ab.shape[0]
    
    for i in range(n):
        for j in range(i + 1, n):
            if matrix_ab[i, j] == 0 and matrix_ab_prime[i, j] == 0:
                kernel.append([i + 1, j + 1])
                
    return kernel


def build_precedence_matrix(ranking: list[int, list[int]], total_objects: int) -> np.ndarray:
    positions = [0] * total_objects
    current_position = 0
    
    for cluster in ranking:
        if not isinstance(cluster, list):
            cluster = [cluster]
        for obj in cluster:
            positions[obj - 1] = current_position
        current_position += 1
    
    matrix = np.zeros((total_objects, total_objects), dtype=int)
    for i in range(total_objects):
        for j in range(total_objects):
            if positions[i] >= positions[j]:
                matrix[i, j] = 1
                
    return matrix

def warshall_algorithm(matrix: np.ndarray) -> np.ndarray:
    n = len(matrix)
    closure = matrix.copy()
    
    for k in range(n):
        for i in range(n):
            for j in range(n):
                closure[i, j] = closure[i, j] or (closure[i, k] and closure[k, j])
    
    return closure


def find_connected_components(closure_matrix: np.ndarray) -> list[list[int]]:
    n = len(closure_matrix)
    visited = [False] * n
    components = []
    
    for i in range(n):
        if not visited[i]:
            component = []
            for j in range(n):
                if closure_matrix[i, j] and closure_matrix[j, i]:
                    component.append(j + 1)
                    visited[j] = True
            components.append(sorted(component))
    
    return components


def topological_sort_clusters(cluster_matrix: np.ndarray, num_clusters: int) -> list[int]:
    visited = [False] * num_clusters
    result_order = []
    
    def dfs(v: int):
        visited[v] = True
        for u in range(num_clusters):
            if cluster_matrix[v, u] == 1 and not visited[u]:
                dfs(u)
        result_order.append(v)
    
    for i in range(num_clusters):
        if not visited[i]:
            dfs(i)
    
    result_order.reverse()
    return result_order


def main(json_string_a: str, json_string_b: str) -> str:
    ranking_a = json.loads(json_string_a)
    ranking_b = json.loads(json_string_b)
    
    all_objects = extract_all_objects([ranking_a, ranking_b])
    
    if not all_objects:
        return json.dumps({"kernel": [], "consistent_ranking": []})
    
    total_objects = max(all_objects)
    
    matrix_a = build_precedence_matrix(ranking_a, total_objects)
    matrix_b = build_precedence_matrix(ranking_b, total_objects)
    
    matrix_ab = matrix_a * matrix_b
    matrix_ab_prime = matrix_a.T * matrix_b.T
    
    kernel = []
    for i in range(total_objects):
        for j in range(i + 1, total_objects):
            if matrix_ab[i, j] == 0 and matrix_ab_prime[i, j] == 0:
                kernel.append([i + 1, j + 1])

    P1 = matrix_a * matrix_b.T
    P2 = matrix_a.T * matrix_b
    P = np.logical_or(P1, P2).astype(int)
    
    C = matrix_a * matrix_b
    
    for pair in kernel:
        i, j = pair[0] - 1, pair[1] - 1
        C[i, j] = 1
        C[j, i] = 1
    
    E = C * C.T
    
    E_star = warshall_algorithm(E)
    
    clusters = find_connected_components(E_star)
    
    num_clusters = len(clusters)
    cluster_matrix = np.zeros((num_clusters, num_clusters), dtype=int)
    
    for i in range(num_clusters):
        for j in range(num_clusters):
            if i != j:
                elem_i = clusters[i][0] - 1
                elem_j = clusters[j][0] - 1
                if C[elem_i, elem_j] == 1:
                    cluster_matrix[i, j] = 1
    
    cluster_order = topological_sort_clusters(cluster_matrix, num_clusters)
    
    consistent_ranking = []
    for idx in cluster_order:
        cluster = clusters[idx]
        if len(cluster) == 1:
            consistent_ranking.append(cluster[0])
        else:
            consistent_ranking.append(cluster)
    
    result = {
        "kernel": kernel,
        "consistent_ranking": consistent_ranking
    }
    
    return json.dumps(result, ensure_ascii=False)


