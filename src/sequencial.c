#include "matrix.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv)
{
    Matrix matrix;
    size_t *labels;
    size_t objects;
    const char *path;
    int result;
    if (argc > 2) {
        fprintf(stderr, "Uso: %s [arquivo]\n", argv[0]);
        return EXIT_FAILURE;
    }
    path = argc == 2 ? argv[1] : "tests/matrizes/exemplo1.txt";
    if (get_matrix(path, &matrix) != 0) return EXIT_FAILURE;
    labels = (size_t *)calloc(matrix.cells, sizeof(size_t));
    if (labels == NULL) {
        perror("calloc rotulos");
        free(matrix.values);
        return EXIT_FAILURE;
    }
    result = get_part_objects(&matrix, 0, matrix.rows, labels, &objects);
    free(labels);
    free(matrix.values);
    if (result != 0) return EXIT_FAILURE;
    printf("%lu\n", (unsigned long)objects);
    return EXIT_SUCCESS;
}
