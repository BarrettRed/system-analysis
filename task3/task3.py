import json

def flatten_ranking(r):
    """Вернуть линейный список всех объектов ранжировки."""
    out = []
    for item in r:
        if isinstance(item, list):
            out.extend(item)
        else:
            out.append(item)
    return out


def build_relation_matrix(ranking):
    """
    Построение матрицы отношений Y (n×n):
    y[i][j] = 1 если xi стоит правее xj или неразличим с ним.
    """
    elems = flatten_ranking(ranking)
    n = max(elems)
    Y = [[0]*n for _ in range(n)]

    # создаём индекс: элемент → позиция кластера
    pos = {}
    for idx, item in enumerate(ranking):
        if isinstance(item, list):
            for x in item:
                pos[x] = idx
        else:
            pos[item] = idx

    # заполнение матрицы
    for i in elems:
        for j in elems:
            if pos[i] > pos[j] or pos[i] == pos[j]:
                Y[i-1][j-1] = 1

    return Y


def matrix_transpose(M):
    return [list(row) for row in zip(*M)]


def matrix_and(A, B):
    return [[A[i][j] & B[i][j] for j in range(len(A))] for i in range(len(A))]


def matrix_or(A, B):
    return [[A[i][j] | B[i][j] for j in range(len(A))] for i in range(len(A))]


def warshall(M):
    """Транзитивное замыкание."""
    n = len(M)
    R = [row[:] for row in M]
    for k in range(n):
        for i in range(n):
            if R[i][k]:
                for j in range(n):
                    R[i][j] = R[i][j] or R[k][j]
    return R


def extract_clusters(E):
    """Компоненты связности в матрице эквивалентности E."""
    n = len(E)
    visited = [False]*n
    clusters = []

    for i in range(n):
        if not visited[i]:
            comp = []
            for j in range(n):
                if E[i][j] == 1 and E[j][i] == 1:
                    comp.append(j+1)
                    visited[j] = True
            clusters.append(comp)

    return clusters


def order_clusters(clusters, C):
    """
    Определение порядка между кластерами:
    кластер A < B если для всех a∈A, b∈B выполняется C[a][b] = 1
    """
    # сортируем пузырьком по отношению порядка C
    changed = True
    while changed:
        changed = False
        for i in range(len(clusters)-1):
            A = clusters[i]
            B = clusters[i+1]
            # если B < A, нужно поменять местами
            better = True
            for a in A:
                for b in B:
                    if C[b-1][a-1] == 0:
                        better = False
                        break
                if not better:
                    break
            if better:
                clusters[i], clusters[i+1] = clusters[i+1], clusters[i]
                changed = True

    return clusters


def json_clusters(clusters):
    """Преобразование кластеров в формат требуемой кластерной ранжировки."""
    out = []
    for cl in clusters:
        if len(cl) == 1:
            out.append(cl[0])
        else:
            out.append(cl)
    return out


def main(jsonA: str, jsonB: str) -> str:
    # читаем ранжировки
    A = json.loads(jsonA)
    B = json.loads(jsonB)

    # 1. Матрицы отношений
    YA = build_relation_matrix(A)
    YB = build_relation_matrix(B)

    YA_t = matrix_transpose(YA)
    YB_t = matrix_transpose(YB)

    # 2. Матрица противоречий
    YAB = matrix_and(YA, YB)
    YAB_t = matrix_and(YA_t, YB_t)

    P = matrix_or(YAB, YAB_t)

    # ядро противоречий = пары (i,j), где pij = 0
    contradictions = []
    n = len(P)
    for i in range(n):
        for j in range(n):
            if i < j and P[i][j] == 0 and P[j][i] == 0:
                contradictions.append([i+1, j+1])

    # 3. Согласованный порядок C = YA ◦ YB
    C = YAB

    # 4. Учет противоречий — делаем симметрию cij=cji=1
    for i, j in contradictions:
        C[i-1][j-1] = 1
        C[j-1][i-1] = 1

    # 5. Эквивалентность E = C ◦ C^T
    Ct = matrix_transpose(C)
    E = matrix_and(C, Ct)

    # транзитивное замыкание
    E_closure = warshall(E)

    # 6. Выделение кластеров
    clusters = extract_clusters(E_closure)

    # 7. Упорядочивание кластеров
    ordered = order_clusters(clusters, C)

    # 8. Формирование результата
    result = {
        "contradictions": contradictions,
        "consensus": json_clusters(ordered)
    }

    return json.dumps(result, ensure_ascii=False)


if __name__=="__main__":
  A = '[1,[2,3],4,[5,6,7],8,9,10]'
  B = '[[1,2],[3,4,5],6,7,9,[8,10]]'

  print(main(A, B))
