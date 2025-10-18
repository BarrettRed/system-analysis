import math
from typing import Tuple, List


def task(s: str, e: str) -> Tuple[float, float]:
    """
    Функция вычисляет энтропию структуры графа и нормированную оценку
    структурной сложности

    Args:
        s (str): CSV-строка со списком рёбер ориентированного дерева, например:
        e (str): идентификатор корневого узла

    Returns:
        Tuple[float, float]: (энтропия, нормированная оценка), округлённые до 1 знака
    """

    # ---------- Парсинг входных данных ----------
    edges = [tuple(map(int, line.split(","))) for line in s.strip().splitlines()]
    nodes = sorted(set(u for u, v in edges) | set(v for u, v in edges))
    n = len(nodes)
    root = int(e)

    # ---------- Построение вспомогательных структур ----------
    # adjacency: список потомков для каждой вершины
    adj = {node: [] for node in nodes}
    for u, v in edges:
        adj[u].append(v)

    # parent: для обратных связей
    parent = {v: u for u, v in edges}

    # уровни для определения r5 (один уровень)
    level = {root: 0}
    queue = [root]
    while queue:
        cur = queue.pop(0)
        for ch in adj[cur]:
            level[ch] = level[cur] + 1
            queue.append(ch)

    # ---------- Определение отношений ----------
    r1 = set(edges)  # непосредственное управление
    r2 = {(b, a) for a, b in r1}  # непосредственное подчинение
    print
    # r3 и r4 — опосредованные (через потомков потомков)
    r3 = set()
    for u in nodes:
        stack = list(adj[u])
        while stack:
            v = stack.pop()
            for ch in adj.get(v, []):
                r3.add((u, ch))
                stack.append(ch)
    r4 = {(b, a) for a, b in r3}

    # r5 — элементы одного уровня (сотрудничество)
    r5 = set()
    for i in nodes:
        for j in nodes:
            if i != j and level[i] == level[j]:
                r5.add((i, j))

    relations = [r1, r2, r3, r4, r5]

    # ---------- Подсчёт исходящих связей ----------
    lij = {node: [0] * 5 for node in nodes}
    for i, r in enumerate(relations):
        for u, v in r:
            lij[u][i] += 1

    # ---------- Энтропия ----------
    H_total = 0.0
    for node in nodes:
        for count in lij[node]:
            if count > 0:
                P = count / (n - 1)
                H_total += -P * math.log2(P)

    # ---------- Нормализация ----------
    k = 5  # число типов отношений
    c = 1 / (math.e * math.log(2))
    H_ref = c * n * k
    h_norm = H_total / H_ref if H_ref != 0 else 0

    # ---------- Округление ----------
    return round(H_total, 1), round(h_norm, 2)


# Пример из условия
if __name__ == "__main__":
    s = "1,2\n1,3\n3,4\n3,5"
    e = "1"
    print(task(s, e))  # Ожидается (6.5, 0.49)
