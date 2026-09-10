def get_object(matrix, row, col, already_visited):
    if (row,col) in already_visited or row < 0 or col < 0 or row >= len(matrix):
        return
    if col >= len(matrix[row]):
        return
    already_visited.append((row,col))
    if matrix[row][col] == 0:
        return
    get_object(matrix, row-1, col-1, already_visited)
    get_object(matrix, row-1, col, already_visited)
    get_object(matrix, row-1, col+1, already_visited)
    get_object(matrix, row, col-1, already_visited)
    get_object(matrix, row, col+1, already_visited)
    get_object(matrix, row+1, col-1, already_visited)
    get_object(matrix, row+1, col, already_visited)
    get_object(matrix, row+1, col+1, already_visited)

def get_objects_number(matrix):
    rows, cols = len(matrix), len(matrix[0])
    already_visited = []
    objs = 0
    for row in range(rows):
        for col in range(cols):
            if (row,col) not in already_visited:
                if matrix[row][col] == 1:
                    objs += 1
                    get_object(matrix, row, col, already_visited)
    return objs