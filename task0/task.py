# task0
#
# Условие:
# Дан ориентированный ациклический граф G = (V, E), где:
#   V -- множество вершин графа,
#   E -- множество рёбер графа.
#
# Каждое ребро ei принадлежит E и описывается парой (vj, vk), где:
#   vj, vk принадлежит V -- вершины графа.
#
# Граф задаётся в виде CSV-файла. Каждая строка файла соответствует одному ребру:
#   начальная вершина, конечная вершина
#
# Пример входных данных (graph.csv):
# 1,2
# 1,3
# 3,4
# 3,5
#
# Задача:
# 1. Написать функцию
#       def main(csv_graph: str) -> list[list[int]]]:
#          ...
#    где csv_graph -- строка (содержимое CSV-файла).
#
# 2. Функция должна возвращать матрицу смежности графа в виде списка списков list[list].
#    - Размер матрицы: n x n, где n = |V| (количество вершин графа).
#    - Элемент matrix[i][j] равен 1, если существует ребро из вершины i в вершину j, и 0, если ребра нет.
#
# Ожидаемый результат:
#  [[0, 1, 1, 0, 0],
#   [1, 0, 0, 0, 0],
#   [1, 0, 0, 1, 1],
#   [0, 0, 1, 0, 0],
#   [0, 0, 1, 0, 0]]

import sys

def main(csv_graph: str) -> list[list[int]]:
    # Читаем содержимое файла как строку
    with open(csv_graph, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Разбираем строку CSV в список рёбер
    data = []
    for line in content.strip().splitlines():
        row = line.strip().split(',')
        data.append(list(map(int, row)))
    
    # Находим максимальный номер вершины
    max_vertex = max(max(row) for row in data)
    
    # Создаем матрицу размером max_vertex x max_vertex
    n = max_vertex
    matrix = [[0] * n for _ in range(n)]
    
    # Заполняем матрицу (учитываем, что индексы с 0, а вершины с 1)
    for start, end in data:
        matrix[start - 1][end - 1] = 1
    
    return matrix


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python main.py <path_to_csv>")
        sys.exit(1)

    path = sys.argv[1]  # путь к CSV из аргументов командной строки
    result = main(path)

    print("Матрица смежности:")
    for row in result:
        print(row)
