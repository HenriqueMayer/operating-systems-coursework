#include <stdio.h>
#include <stdlib.h>

/*
 * Lê a matriz do arquivo.
 *
 * Formato esperado:
 *
 * primeira linha: dimensões (não utilizada diretamente)
 * demais linhas: matriz binária
 */
int **get_matrix(const char *path, int *rows, int *cols)
{
    FILE *file;
    int **matrix;
    int i;
    int j;

    file = fopen(path, "r");

    if (file == NULL) {
        printf("Erro ao abrir o arquivo.\n");
        return NULL;
    }

    /*
     * O código Python ignora a primeira linha.
     *
     * Aqui também lemos as dimensões dessa linha.
     */
    if (fscanf(file, "%d %d", rows, cols) != 2) {
        printf("Erro ao ler as dimensoes da matriz.\n");
        fclose(file);
        return NULL;
    }

    matrix = (int **) malloc(
        (size_t)(*rows) * sizeof(int *)
    );

    if (matrix == NULL) {
        printf("Erro de alocacao.\n");
        fclose(file);
        return NULL;
    }

    for (i = 0; i < *rows; i++) {
        matrix[i] = (int *) malloc(
            (size_t)(*cols) * sizeof(int)
        );

        if (matrix[i] == NULL) {
            printf("Erro de alocacao.\n");

            for (j = 0; j < i; j++) {
                free(matrix[j]);
            }

            free(matrix);
            fclose(file);

            return NULL;
        }
    }

    for (i = 0; i < *rows; i++) {
        for (j = 0; j < *cols; j++) {
            if (fscanf(file, "%d", &matrix[i][j]) != 1) {
                printf("Erro ao ler a matriz.\n");

                for (j = 0; j < *rows; j++) {
                    free(matrix[j]);
                }

                free(matrix);
                fclose(file);

                return NULL;
            }
        }
    }

    fclose(file);

    return matrix;
}


/*
 * Libera a matriz.
 */
void free_matrix(int **matrix, int rows)
{
    int i;

    for (i = 0; i < rows; i++) {
        free(matrix[i]);
    }

    free(matrix);
}


/*
 * Flood fill recursivo.
 *
 * Verifica as 8 posições vizinhas:
 *
 * (-1,-1) (-1,0) (-1,+1)
 * ( 0,-1)         ( 0,+1)
 * (+1,-1) (+1,0) (+1,+1)
 */
void get_object(
    int **matrix,
    int rows,
    int cols,
    int row,
    int col,
    int **already_visited
)
{
    /*
     * Verifica limites da matriz.
     */
    if (row < 0 ||
        col < 0 ||
        row >= rows ||
        col >= cols) {
        return;
    }

    /*
     * Já visitado.
     */
    if (already_visited[row][col]) {
        return;
    }

    /*
     * Marca como visitado.
     *
     * O Python fazia isso antes de verificar
     * se a célula era 0.
     */
    already_visited[row][col] = 1;

    /*
     * Fundo.
     */
    if (matrix[row][col] == 0) {
        return;
    }

    /*
     * 8 vizinhos.
     */
    get_object(
        matrix, rows, cols,
        row - 1, col - 1,
        already_visited
    );

    get_object(
        matrix, rows, cols,
        row - 1, col,
        already_visited
    );

    get_object(
        matrix, rows, cols,
        row - 1, col + 1,
        already_visited
    );

    get_object(
        matrix, rows, cols,
        row, col - 1,
        already_visited
    );

    get_object(
        matrix, rows, cols,
        row, col + 1,
        already_visited
    );

    get_object(
        matrix, rows, cols,
        row + 1, col - 1,
        already_visited
    );

    get_object(
        matrix, rows, cols,
        row + 1, col,
        already_visited
    );

    get_object(
        matrix, rows, cols,
        row + 1, col + 1,
        already_visited
    );
}


/*
 * Conta os objetos da matriz.
 */
int get_objects_number(
    int **matrix,
    int rows,
    int cols
)
{
    int **already_visited;
    int i;
    int j;
    int objs;

    /*
     * Matriz para marcar células visitadas.
     */
    already_visited = (int **) malloc(
        (size_t)rows * sizeof(int *)
    );

    if (already_visited == NULL) {
        return -1;
    }

    for (i = 0; i < rows; i++) {
        already_visited[i] = (int *) calloc(
            (size_t)cols,
            sizeof(int)
        );

        if (already_visited[i] == NULL) {
            for (j = 0; j < i; j++) {
                free(already_visited[j]);
            }

            free(already_visited);

            return -1;
        }
    }

    objs = 0;

    /*
     * Equivalente a:
     *
     * for row in range(rows):
     *     for col in range(cols):
     */
    for (i = 0; i < rows; i++) {
        for (j = 0; j < cols; j++) {

            /*
             * Se ainda não visitamos essa célula
             * e ela pertence ao primeiro plano,
             * encontramos um novo objeto.
             */
            if (!already_visited[i][j] &&
                matrix[i][j] == 1) {

                objs++;

                get_object(
                    matrix,
                    rows,
                    cols,
                    i,
                    j,
                    already_visited
                );
            }
        }
    }

    /*
     * Libera a matriz de visitados.
     */
    for (i = 0; i < rows; i++) {
        free(already_visited[i]);
    }

    free(already_visited);

    return objs;
}


int main(int argc, char **argv)
{
    int **matrix;
    int rows;
    int cols;
    int objects;

    if (argc != 2) {
        printf("Uso: %s <arquivo>\n", argv[0]);
        return EXIT_FAILURE;
    }

    matrix = get_matrix(
        argv[1],
        &rows,
        &cols
    );

    if (matrix == NULL) {
        return EXIT_FAILURE;
    }

    objects = get_objects_number(
        matrix,
        rows,
        cols
    );

    if (objects < 0) {
        free_matrix(matrix, rows);
        return EXIT_FAILURE;
    }

    printf("Objetos: %d\n", objects);

    free_matrix(matrix, rows);

    return EXIT_SUCCESS;
}