from typing import List, Tuple, Dict


def main(s: str, e: str) -> Tuple[
    List[List[bool]],
    List[List[bool]],
    List[List[bool]],
    List[List[bool]],
    List[List[bool]]
]:
    """
    Построение матриц смежности для пяти предикатов на дереве.

    Аргументы:
        s: str - CSV-строка рёбер в формате "1,2\n1,3\n3,4..."
        e: str - идентификатор корневого узла (строка)

    Возвращает:
        Tuple из пяти матриц смежности (каждая как List[List[bool]]):
        r1 - непосредственное управление (parent -> child)
        r2 - непосредственное подчинение (child -> parent)
        r3 - опосредованное управление (ancestor -> descendant, но не parent)
        r4 - опосредованное подчинение (descendant -> ancestor, но не child)
        r5 - соподчинение (x,y имеют одного родителя)
    """

    # --- Шаг 1. Разбор входных данных ---
    edges = []
    for line in s.strip().split("\n"):
        u, v = line.strip().split(",")
        edges.append((u.strip(), v.strip()))

    # --- Шаг 2. Определим множество вершин ---
    vertices = set()
    for u, v in edges:
        vertices.add(u)
        vertices.add(v)
    vertices = sorted(vertices, key=lambda x: int(x))  # сортируем по числовому значению
    n = len(vertices)

    # Соответствие: вершина -> индекс в матрице
    idx: Dict[str, int] = {v: i for i, v in enumerate(vertices)}

    # --- Шаг 3. Строим дерево (parent -> children) и обратное (child -> parent) ---
    children: Dict[str, List[str]] = {v: [] for v in vertices}
    parent: Dict[str, str] = {}

    for u, v in edges:
        children[u].append(v)
        parent[v] = u

    # --- Шаг 4. Инициализация матриц ---
    r1 = [[False] * n for _ in range(n)]  # parent -> child
    r2 = [[False] * n for _ in range(n)]  # child -> parent
    r3 = [[False] * n for _ in range(n)]  # ancestor -> descendant (not parent)
    r4 = [[False] * n for _ in range(n)]  # descendant -> ancestor (not child)
    r5 = [[False] * n for _ in range(n)]  # siblings

    # --- Шаг 5. Заполняем r1 и r2 ---
    for u, vs in children.items():
        for v in vs:
            i, j = idx[u], idx[v]
            r1[i][j] = True  # u -> v (непосредственное управление)
            r2[j][i] = True  # v -> u (непосредственное подчинение)

    # --- Шаг 6. Поиск всех предков и потомков ---
    def dfs_ancestors(node: str) -> List[str]:
        """Возвращает список всех предков вершины node"""
        result = []
        cur = node
        while cur in parent:
            p = parent[cur]
            result.append(p)
            cur = p
        return result

    def dfs_descendants(node: str) -> List[str]:
        """Возвращает список всех потомков вершины node"""
        result = []

        def dfs(u: str):
            for v in children[u]:
                result.append(v)
                dfs(v)

        dfs(node)
        return result

    # --- Шаг 7. Заполняем r3 и r4 ---
    for v in vertices:
        i = idx[v]
        # все предки v
        ancestors = dfs_ancestors(v)
        for a in ancestors:
            j = idx[a]
            if parent[v] == a:
                # это непосредственный родитель => не учитываем в r3/r4
                continue
            r3[j][i] = True  # предок -> потомок (опосредованное управление)
            r4[i][j] = True  # потомок -> предок (опосредованное подчинение)

    # --- Шаг 8. Заполняем r5 (соподчинение) ---
    for u, vs in children.items():
        for i1 in range(len(vs)):
            for i2 in range(len(vs)):
                if i1 != i2:
                    r5[idx[vs[i1]]][idx[vs[i2]]] = True

    return r1, r2, r3, r4, r5


# --- Пример использования ---
if __name__ == "__main__":
    s = "1,2\n1,3\n3,4\n3,5\n5,6\n6,7"
    e = "1"
    matrices = main(s, e)
    for k, m in enumerate(matrices, start=1):
        print(f"r{k}:")
        for row in m:
            print(row)
        print()
