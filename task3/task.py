import json
import numpy as np


def read_json(file_path: str) -> str:
    content = []
    with open(file_path, 'r') as fh:
        for segment in fh:
            content.append(segment)
    return ''.join(content)


def build_precedence_matrix(ranking: list[int, list[int]], total_objects: int) -> np.ndarray:
    idx_mapping = {}
    lvl = 0
    
    for group in ranking:
        items = group if isinstance(group, (list, tuple)) else [group]
        for item in items:
            idx_mapping[item - 1] = lvl
        lvl += 1
    
    col_indices = np.arange(total_objects)
    row_levels = np.array([idx_mapping.get(i, 0) for i in range(total_objects)])
    
    precedence = (row_levels[:, None] >= row_levels[None, :]).astype(int)
    return precedence


def extract_all_objects(rankings: list[list[int, list[int]]]) -> set:
    collected = set()
    for rnk in rankings:
        for entry in rnk:
            elements = entry if hasattr(entry, '__iter__') and not isinstance(entry, (str, bytes)) else [entry]
            collected.update(elements)
    return collected


def find_contradiction_kernel(matrix_ab: np.ndarray, matrix_ab_prime: np.ndarray) -> list[list[int]]:
    discrepancies = []
    dim = matrix_ab.shape[0]
    
    mask = (matrix_ab == 0) & (matrix_ab_prime == 0)
    for i in range(dim):
        for j in range(i + 1, dim):
            if mask[i, j]:
                discrepancies.append([i + 1, j + 1])
                
    return discrepancies


def warshall_algorithm(matrix: np.ndarray) -> np.ndarray:
    n_dim = matrix.shape[0]
    transitive = matrix.astype(bool).copy()
    
    for intermediate in range(n_dim):
        transitive |= transitive[:, intermediate][:, None] & transitive[intermediate, :]
    
    return transitive.astype(int)


def find_connected_components(closure_matrix: np.ndarray) -> list[list[int]]:
    size = closure_matrix.shape[0]
    marked = [False] * size
    groups = []
    
    closure_bool = closure_matrix.astype(bool)
    
    for start in range(size):
        if marked[start]:
            continue
        component = []
        for vertex in range(size):
            if closure_bool[start, vertex] and closure_bool[vertex, start]:
                component.append(vertex + 1)
                marked[vertex] = True
        if component:
            groups.append(sorted(component))
    
    return groups


def topological_sort_clusters(cluster_matrix: np.ndarray, num_clusters: int) -> list[int]:
    seen = [False] * num_clusters
    stack = []
    
    def explore(node: int):
        seen[node] = True
        neighbors = np.where(cluster_matrix[node] == 1)[0]
        for nb in neighbors:
            if not seen[nb]:
                explore(nb)
        stack.append(node)
    
    for v in range(num_clusters):
        if not seen[v]:
            explore(v)
    
    return stack[::-1]


def main(json_string_a: str, json_string_b: str) -> str:
    data_a = json.loads(json_string_a)
    data_b = json.loads(json_string_b)
    
    universe = extract_all_objects([data_a, data_b])
    
    if not universe:
        return json.dumps({"kernel": [], "consistent_ranking": []})
    
    max_obj = max(universe)
    
    mat_a = build_precedence_matrix(data_a, max_obj)
    mat_b = build_precedence_matrix(data_b, max_obj)
    
    intersection_ab = mat_a * mat_b
    intersection_ab_t = mat_a.T * mat_b.T
    
    conflict_kernel = []
    for x in range(max_obj):
        for y in range(x + 1, max_obj):
            if not intersection_ab[x, y] and not intersection_ab_t[x, y]:
                conflict_kernel.append([x + 1, y + 1])

    partial_1 = mat_a * mat_b.T
    partial_2 = mat_a.T * mat_b
    aggregation = np.logical_or(partial_1, partial_2).astype(int)
    
    combined = mat_a * mat_b
    
    for pair in conflict_kernel:
        u, v = pair[0] - 1, pair[1] - 1
        combined[u, v] = combined[v, u] = 1
    
    equivalence = combined * combined.T
    
    star_closure = warshall_algorithm(equivalence)
    
    components = find_connected_components(star_closure)
    
    cluster_cnt = len(components)
    adjacency = np.zeros((cluster_cnt, cluster_cnt), dtype=int)
    
    for p in range(cluster_cnt):
        for q in range(cluster_cnt):
            if p != q:
                repr_p = components[p][0] - 1
                repr_q = components[q][0] - 1
                adjacency[p, q] = int(combined[repr_p, repr_q] == 1)
    
    ordering = topological_sort_clusters(adjacency, cluster_cnt)
    
    final_ranking = []
    for pos in ordering:
        group = components[pos]
        final_ranking.append(group[0] if len(group) == 1 else group)
    
    output = {
        "kernel": conflict_kernel,
        "consistent_ranking": final_ranking
    }
    
    return json.dumps(output, ensure_ascii=False)



if __name__ == "__main__":
    json_string_a: str = read_json("task3/ranking-A.json")
    json_string_b: str = read_json("task3/ranking-B.json")
    json_string_c: str = read_json("task3/ranking-C.json")
    
    result_ab = json.loads(main(json_string_a, json_string_b))
    print(f"AB:\nЯдро противоречий: {result_ab['kernel']}\nСогласованная кластерная ранжировка: {result_ab['consistent_ranking']}")
    
    result_ac = json.loads(main(json_string_a, json_string_c))
    print(f"AC:\nЯдро противоречий: {result_ac['kernel']}\nСогласованная кластерная ранжировка: {result_ac['consistent_ranking']}")

    result_bc = json.loads(main(json_string_b, json_string_c))
    print(f"BC:\nЯдро противоречий: {result_bc['kernel']}\nСогласованная кластерная ранжировка: {result_bc['consistent_ranking']}")