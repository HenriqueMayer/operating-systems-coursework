from concurrent.futures import ProcessPoolExecutor

from sequencial import get_matrix


def get_object(matrix, row, col, labels, label):
    # Explora os oito vizinhos apenas dentro da faixa deste processo.
    stack = [(row, col)]
    labels[row][col] = label
    while stack:
        row, col = stack.pop()
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = row + dr, col + dc
                if nr < 0 or nr >= len(matrix):
                    continue
                if nc < 0 or nc >= len(matrix[0]):
                    continue
                if matrix[nr][nc] == 1 and labels[nr][nc] == 0:
                    labels[nr][nc] = label
                    stack.append((nr, nc))


def get_part_objects(matrix):
    rows, cols = len(matrix), len(matrix[0])
    labels = [[0] * cols for _ in range(rows)]
    objs = 0
    for row in range(rows):
        for col in range(cols):
            if matrix[row][col] == 1 and labels[row][col] == 0:
                objs += 1
                get_object(matrix, row, col, labels, objs)
    # Só as bordas são necessárias para consolidar faixas vizinhas.
    return objs, labels[0], labels[-1]


def get_root(parents, label):
    while parents[label] != label:
        parents[label] = parents[parents[label]]
        label = parents[label]
    return label


def get_objects_number(matrix, processes=2):
    if not isinstance(processes, int) or processes < 1:
        raise ValueError("O numero de processos deve ser maior que zero.")
    if not matrix or not matrix[0]:
        raise ValueError("A matriz deve possuir linhas e colunas.")
    rows, cols = len(matrix), len(matrix[0])
    if any(len(row) != cols for row in matrix):
        raise ValueError("As linhas devem possuir o mesmo tamanho.")
    if any(value not in (0, 1) for row in matrix for value in row):
        raise ValueError("A matriz deve conter apenas 0 e 1.")

    processes = min(processes, rows)
    base_rows, extra_rows = divmod(rows, processes)
    parts = []
    start = 0
    for index in range(processes):
        end = start + base_rows + (index < extra_rows)
        parts.append(matrix[start:end])
        start = end

    # Cada processo rotula os objetos da sua faixa, sem dados compartilhados.
    with ProcessPoolExecutor(max_workers=processes) as pool:
        results = list(pool.map(get_part_objects, parts))

    objs = sum(result[0] for result in results)
    parents = {}
    sizes = {}
    for index, (count, _, _) in enumerate(results):
        for label in range(1, count + 1):
            key = (index, label)
            parents[key] = key
            sizes[key] = 1

    # Une componentes nas fronteiras verticais e diagonais entre faixas.
    for index in range(len(results) - 1):
        upper = results[index][2]
        lower = results[index + 1][1]
        for col, label in enumerate(upper):
            if label == 0:
                continue
            for nc in range(max(0, col - 1), min(cols, col + 2)):
                if lower[nc] == 0:
                    continue
                a = get_root(parents, (index, label))
                b = get_root(parents, (index + 1, lower[nc]))
                if a != b:
                    if sizes[a] < sizes[b]:
                        a, b = b, a
                    parents[b] = a
                    sizes[a] += sizes[b]
                    objs -= 1
    return objs


if __name__ == "__main__":
    print(get_objects_number(get_matrix("tests/matrizes/exemplo1.txt")))
