import json
import numpy as np
from collections import defaultdict

def parse_json_document(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read().strip()

def compute_transitive_closure(adjacency):
    size = adjacency.shape[0]
    R = adjacency.astype(bool).copy()
    
    for pivot in range(size):
        for src in range(size):
            if R[src, pivot]:
                for dst in range(size):
                    R[src, dst] = R[src, dst] or R[pivot, dst]
    return R.astype(int)

def extract_equivalence_groups(relation):
    n = relation.shape[0]
    processed = [False] * n
    groups = []
    
    for idx in range(n):
        if not processed[idx]:
            equivalent_set = set()
            for other in range(n):
                if relation[idx, other] and relation[other, idx]:
                    equivalent_set.add(other)
                    processed[other] = True
            if equivalent_set:
                groups.append(sorted([x+1 for x in equivalent_set]))
    return groups

def analyze_rankings(data1, data2):
    rank1 = json.loads(data1)
    rank2 = json.loads(data2)
    
    elements = set()
    for ranking in (rank1, rank2):
        for item in ranking:
            elements.update(item if isinstance(item, list) else [item])
    
    if not elements:
        return {"contradictions": [], "merged_ranking": []}
    
    max_elem = max(elements)
    
    def construct_precedence_matrix(ranking):
        positions = np.zeros(max_elem, dtype=int)
        level = 0
        for cluster in ranking:
            items = cluster if isinstance(cluster, list) else [cluster]
            for obj in items:
                positions[obj-1] = level
            level += 1
        
        mat = np.zeros((max_elem, max_elem), dtype=int)
        for i in range(max_elem):
            for j in range(max_elem):
                mat[i, j] = 1 if positions[i] >= positions[j] else 0
        return mat
    
    M1 = construct_precedence_matrix(rank1)
    M2 = construct_precedence_matrix(rank2)
    
    common_precedence = M1 * M2
    M1_transposed = M1.T
    M2_transposed = M2.T
    
    divergence_pairs = []
    for i in range(max_elem):
        for j in range(i+1, max_elem):
            if (common_precedence[i, j] == 0 and 
                common_precedence[j, i] == 0 and
                M1_transposed[i, j] * M2_transposed[i, j] == 0):
                divergence_pairs.append([i+1, j+1])
    
    conflict_matrix = M1 * M2_transposed | M1_transposed * M2
    
    base_relation = M1 * M2
    
    for a, b in divergence_pairs:
        i, j = a-1, b-1
        base_relation[i, j] = base_relation[j, i] = 1
    
    symmetric_relation = base_relation * base_relation.T
    
    transitive_closure = compute_transitive_closure(symmetric_relation)
    
    equivalence_classes = extract_equivalence_groups(transitive_closure)
    
    if not equivalence_classes:
        return {"contradictions": divergence_pairs, "merged_ranking": []}
    
    class_count = len(equivalence_classes)
    ordering_matrix = np.zeros((class_count, class_count), dtype=int)
    
    for idx1 in range(class_count):
        for idx2 in range(class_count):
            if idx1 != idx2:
                elem1 = equivalence_classes[idx1][0] - 1
                elem2 = equivalence_classes[idx2][0] - 1
                if base_relation[elem1, elem2]:
                    ordering_matrix[idx1, idx2] = 1
    
    visited = [False] * class_count
    sorted_indices = []
    
    def dfs(node):
        visited[node] = True
        for neighbor in range(class_count):
            if ordering_matrix[node, neighbor] and not visited[neighbor]:
                dfs(neighbor)
        sorted_indices.append(node)
    
    for node in range(class_count):
        if not visited[node]:
            dfs(node)
    
    sorted_indices.reverse()
    
    final_ranking = []
    for class_idx in sorted_indices:
        group = equivalence_classes[class_idx]
        final_ranking.append(group[0] if len(group) == 1 else group)
    
    return {
        "contradictions": divergence_pairs,
        "merged_ranking": final_ranking
    }

def execute_comparison():
    input_files = ['range_a.json', 'range_b.json', 'range_c.json']
    results = {}
    
    for i in range(len(input_files)):
        for j in range(i+1, len(input_files)):
            data1 = parse_json_document(input_files[i])
            data2 = parse_json_document(input_files[j])
            key = f"{input_files[i][:-5]}_{input_files[j][:-5]}"
            results[key] = analyze_rankings(data1, data2)
    
    return results

if __name__ == "__main__":
    comparisons = execute_comparison()
    
    print("РАНЖИРОВКИ - АНАЛИЗ СРАВНЕНИЯ")
    
    for comp_name, result in comparisons.items():
        print(f"\n{comp_name.replace('_', ' vs ')}")
        print(f"Противоречивые пары: {result['contradictions']}")
        print(f"Результирующий порядок: {result['merged_ranking']}")