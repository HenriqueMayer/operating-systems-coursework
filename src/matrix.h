#ifndef MATRIX_H
#define MATRIX_H
#include <stddef.h>
typedef struct {
    size_t rows;
    size_t cols;
    size_t cells;
    unsigned char *values;
} Matrix;
int get_matrix(const char *path, Matrix *matrix);
/* Rotula uma faixa. Cada componente usa como ID o indice inicial + 1. */
int get_part_objects(const Matrix *matrix, size_t start, size_t end,
                     size_t *labels, size_t *objects);
int get_processes(const char *text, size_t *processes);
#endif
