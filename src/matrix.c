#include "matrix.h"
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <errno.h>
#include <limits.h>
#include <string.h>

/* Le tokens limitados, evitando conversoes numericas fora do intervalo. */
static int read_number(FILE *file, unsigned long *value)
{
    char token[64];
    char *end;
    size_t length;
    int ch;
    do { ch = fgetc(file); } while (ch != EOF && isspace(ch));
    if (ch == EOF) return 0;
    length = 0;
    while (ch != EOF && !isspace(ch)) {
        if (length + 1 >= sizeof(token) || !isdigit(ch)) return -1;
        token[length++] = (char)ch;
        ch = fgetc(file);
    }
    token[length] = '\0';
    errno = 0;
    *value = strtoul(token, &end, 10);
    return errno == ERANGE || *end != '\0' ? -1 : 1;
}

int get_processes(const char *text, size_t *processes)
{
    const char *p;
    char *end;
    unsigned long value;
    if (*text == '\0') return -1;
    for (p = text; *p; p++) if (!isdigit((unsigned char)*p)) return -1;
    errno = 0;
    value = strtoul(text, &end, 10);
    if (errno == ERANGE || *end || value == 0 || value > (size_t)-1)
        return -1;
    *processes = (size_t)value;
    return 0;
}

int get_matrix(const char *path, Matrix *matrix)
{
    FILE *file;
    unsigned long rows;
    unsigned long cols;
    unsigned long value;
    size_t i;
    int result;
    memset(matrix, 0, sizeof(*matrix));
    file = fopen(path, "r");
    if (file == NULL) { perror(path); return -1; }
    result = -1;
    if (read_number(file, &rows) != 1 || read_number(file, &cols) != 1 ||
        rows == 0 || cols == 0 || rows > (size_t)-1 || cols > (size_t)-1) {
        fprintf(stderr, "Dimensoes invalidas.\n");
        goto done;
    }
    matrix->rows = (size_t)rows;
    matrix->cols = (size_t)cols;
    /* Labels e pilha utilizam size_t: validar antes de multiplicar. */
    if (matrix->rows > ((size_t)-1) / matrix->cols ||
        matrix->rows * matrix->cols > ((size_t)-1) / sizeof(size_t)) {
        fprintf(stderr, "Matriz excede o limite de tamanho.\n");
        goto done;
    }
    matrix->cells = matrix->rows * matrix->cols;
    matrix->values = (unsigned char *)malloc(matrix->cells);
    if (matrix->values == NULL) { perror("malloc matriz"); goto done; }
    for (i = 0; i < matrix->cells; i++) {
        if (read_number(file, &value) != 1 || value > 1) {
            fprintf(stderr, "Matriz incompleta ou valor diferente de 0 e 1.\n");
            goto done;
        }
        matrix->values[i] = (unsigned char)value;
    }
    if (read_number(file, &value) != 0 || ferror(file)) {
        fprintf(stderr, "Dados excedentes ou erro de leitura.\n");
        goto done;
    }
    result = 0;
done:
    if (fclose(file) != 0) { perror("fclose"); result = -1; }
    if (result != 0) { free(matrix->values); matrix->values = NULL; }
    return result;
}

int get_part_objects(const Matrix *matrix, size_t start, size_t end,
                     size_t *labels, size_t *objects)
{
    size_t *stack;
    size_t first;
    size_t limit;
    size_t cell;
    size_t current;
    size_t top;
    size_t row;
    size_t col;
    size_t nr;
    size_t nc;
    size_t next;
    size_t label;
    int dr;
    int dc;
    first = start * matrix->cols;
    limit = end * matrix->cols;
    stack = (size_t *)malloc((limit - first) * sizeof(size_t));
    if (stack == NULL) { perror("malloc pilha"); return -1; }
    *objects = 0;
    for (cell = first; cell < limit; cell++) {
        if (!matrix->values[cell] || labels[cell - first]) continue;
        (*objects)++;
        label = cell + 1;
        labels[cell - first] = label;
        top = 0;
        stack[top++] = cell;
        while (top) {
            current = stack[--top];
            row = current / matrix->cols;
            col = current % matrix->cols;
            for (dr = -1; dr <= 1; dr++) {
                if ((dr < 0 && row == start) ||
                    (dr > 0 && row + 1 == end)) continue;
                nr = dr < 0 ? row - 1 : (dr > 0 ? row + 1 : row);
                for (dc = -1; dc <= 1; dc++) {
                    if ((dc < 0 && col == 0) ||
                        (dc > 0 && col + 1 == matrix->cols)) continue;
                    nc = dc < 0 ? col - 1 : (dc > 0 ? col + 1 : col);
                    next = nr * matrix->cols + nc;
                    if (matrix->values[next] && !labels[next - first]) {
                        labels[next - first] = label;
                        stack[top++] = next;
                    }
                }
            }
        }
    }
    free(stack);
    return 0;
}
