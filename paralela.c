#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

typedef struct {
    int *matrix;
    int *labels;
    int rows;
    int cols;
    int thread_id;
    int start_row;
    int end_row;
    int max_local_labels;
} ThreadData;

typedef struct {
    int *parent;
    int *rank;
    int size;
} UnionFind;

/*
 * Retorna o índice linear da posição (row, col).
 */
static int index_of(int row, int col, int cols)
{
    return row * cols + col;
}

/*
 * Union-Find: encontra o representante do conjunto.
 */
static int uf_find(UnionFind *uf, int x)
{
    if (uf->parent[x] != x) {
        uf->parent[x] = uf_find(uf, uf->parent[x]);
    }

    return uf->parent[x];
}

/*
 * Union-Find: une dois conjuntos.
 */
static void uf_union(UnionFind *uf, int a, int b)
{
    int root_a;
    int root_b;

    root_a = uf_find(uf, a);
    root_b = uf_find(uf, b);

    if (root_a == root_b) {
        return;
    }

    if (uf->rank[root_a] < uf->rank[root_b]) {
        uf->parent[root_a] = root_b;
    } else if (uf->rank[root_a] > uf->rank[root_b]) {
        uf->parent[root_b] = root_a;
    } else {
        uf->parent[root_b] = root_a;
        uf->rank[root_a]++;
    }
}

/*
 * Flood fill iterativo.
 *
 * O objeto é explorado apenas dentro da faixa de linhas
 * pertencente à thread.
 */
static void flood_fill(
    ThreadData *data,
    int start_row,
    int start_col,
    int local_label,
    int *stack
)
{
    int top;
    int row;
    int col;
    int nr;
    int nc;
    int current;
    int k;

    /*
     * 8 vizinhos:
     *
     * (-1,-1) (-1,0) (-1,+1)
     * ( 0,-1)         ( 0,+1)
     * (+1,-1) (+1,0) (+1,+1)
     */
    static const int dr[8] = {
        -1, -1, -1,
         0,  0,
         1,  1,  1
    };

    static const int dc[8] = {
        -1,  0,  1,
        -1,  1,
        -1,  0,  1
    };

    top = 0;

    current = index_of(start_row, start_col, data->cols);

    data->labels[current] = local_label;
    stack[top] = current;
    top++;

    while (top > 0) {
        top--;

        current = stack[top];

        row = current / data->cols;
        col = current % data->cols;

        for (k = 0; k < 8; k++) {
            nr = row + dr[k];
            nc = col + dc[k];

            /*
             * Não podemos sair da faixa da thread.
             */
            if (nr < data->start_row || nr >= data->end_row) {
                continue;
            }

            if (nc < 0 || nc >= data->cols) {
                continue;
            }

            if (data->matrix[index_of(nr, nc, data->cols)] == 0) {
                continue;
            }

            if (data->labels[index_of(nr, nc, data->cols)] != 0) {
                continue;
            }

            data->labels[index_of(nr, nc, data->cols)] = local_label;

            stack[top] = index_of(nr, nc, data->cols);
            top++;
        }
    }
}

/*
 * Função executada por cada thread.
 */
static void *worker(void *argument)
{
    ThreadData *data;
    int *stack;
    int row;
    int col;
    int local_label;
    int global_label;

    data = (ThreadData *) argument;

    /*
     * Uma célula por posição é suficiente para o stack.
     */
    stack = (int *) malloc(
        (size_t)(data->rows * data->cols) * sizeof(int)
    );

    if (stack == NULL) {
        fprintf(stderr, "Erro ao alocar stack da thread %d.\n",
                data->thread_id);
        pthread_exit(NULL);
    }

    local_label = 0;

    for (row = data->start_row; row < data->end_row; row++) {
        for (col = 0; col < data->cols; col++) {
            if (data->matrix[index_of(row, col, data->cols)] == 0) {
                continue;
            }

            if (data->labels[index_of(row, col, data->cols)] != 0) {
                continue;
            }

            local_label++;

            /*
             * Cada thread possui um intervalo próprio de IDs.
             *
             * Exemplo:
             * thread 0 -> 1, 2, 3, ...
             * thread 1 -> MAX+1, MAX+2, ...
             */
            global_label =
                data->thread_id * data->max_local_labels
                + local_label;

            flood_fill(
                data,
                row,
                col,
                global_label,
                stack
            );
        }
    }

    free(stack);

    pthread_exit(NULL);
}

/*
 * Verifica uma fronteira entre duas faixas de linhas.
 *
 * Como temos conectividade 8, uma célula na última linha da
 * faixa superior pode se conectar às três células:
 *
 *       X X X
 *         X
 *
 * na primeira linha da faixa inferior.
 */
static void consolidate_boundary(
    int *labels,
    int cols,
    int upper_row,
    UnionFind *uf
)
{
    int col;
    int upper_label;
    int lower_label;

    /*
     * Compara:
     *
     * (upper_row, col)
     *
     * com:
     *
     * (upper_row + 1, col - 1)
     * (upper_row + 1, col)
     * (upper_row + 1, col + 1)
     */
    for (col = 0; col < cols; col++) {
        upper_label = labels[
            index_of(upper_row, col, cols)
        ];

        if (upper_label == 0) {
            continue;
        }

        if (col > 0) {
            lower_label = labels[
                index_of(upper_row + 1, col - 1, cols)
            ];

            if (lower_label != 0) {
                uf_union(uf, upper_label, lower_label);
            }
        }

        lower_label = labels[
            index_of(upper_row + 1, col, cols)
        ];

        if (lower_label != 0) {
            uf_union(uf, upper_label, lower_label);
        }

        if (col + 1 < cols) {
            lower_label = labels[
                index_of(upper_row + 1, col + 1, cols)
            ];

            if (lower_label != 0) {
                uf_union(uf, upper_label, lower_label);
            }
        }
    }
}

/*
 * Conta os representantes dos componentes depois da
 * consolidação.
 */
static int count_components(
    int *matrix,
    int *labels,
    int rows,
    int cols,
    UnionFind *uf,
    int max_labels
)
{
    int *seen;
    int i;
    int root;
    int count;

    seen = (int *) calloc(
        (size_t)max_labels,
        sizeof(int)
    );

    if (seen == NULL) {
        fprintf(stderr, "Erro ao alocar vetor de componentes.\n");
        return -1;
    }

    count = 0;

    for (i = 0; i < rows * cols; i++) {
        if (matrix[i] == 0) {
            continue;
        }

        if (labels[i] == 0) {
            continue;
        }

        root = uf_find(uf, labels[i]);

        if (!seen[root]) {
            seen[root] = 1;
            count++;
        }
    }

    free(seen);

    return count;
}

int main(int argc, char **argv)
{
    int rows;
    int cols;
    int num_threads;

    int *matrix;
    int *labels;

    pthread_t *threads;
    ThreadData *thread_data;

    UnionFind uf;

    int max_local_labels;
    int max_labels;

    int i;
    int row;
    int col;
    int start_row;
    int end_row;
    int base_rows;
    int extra_rows;

    int result;

    if (argc != 2) {
        fprintf(
            stderr,
            "Uso: %s <numero_de_threads>\n",
            argv[0]
        );
        return EXIT_FAILURE;
    }

    num_threads = atoi(argv[1]);

    if (num_threads <= 0) {
        fprintf(
            stderr,
            "O numero de threads deve ser maior que zero.\n"
        );
        return EXIT_FAILURE;
    }

    /*
     * Entrada:
     *
     * linhas colunas
     * matriz...
     *
     * Exemplo:
     *
     * 5 5
     * 1 1 0 0 0
     * 1 1 0 0 0
     * 0 0 0 1 0
     * 0 0 0 1 0
     * 1 0 0 0 0
     */
    if (scanf("%d %d", &rows, &cols) != 2) {
        fprintf(stderr, "Erro ao ler dimensoes da matriz.\n");
        return EXIT_FAILURE;
    }

    if (rows <= 0 || cols <= 0) {
        fprintf(stderr, "Dimensoes invalidas.\n");
        return EXIT_FAILURE;
    }

    /*
     * Não faz sentido criar mais threads que linhas.
     */
    if (num_threads > rows) {
        num_threads = rows;
    }

    matrix = (int *) malloc(
        (size_t)(rows * cols) * sizeof(int)
    );

    labels = (int *) calloc(
        (size_t)(rows * cols),
        sizeof(int)
    );

    if (matrix == NULL || labels == NULL) {
        fprintf(stderr, "Erro ao alocar matriz.\n");

        free(matrix);
        free(labels);

        return EXIT_FAILURE;
    }

    for (row = 0; row < rows; row++) {
        for (col = 0; col < cols; col++) {
            if (scanf(
                    "%d",
                    &matrix[index_of(row, col, cols)]
                ) != 1) {

                fprintf(stderr, "Erro ao ler matriz.\n");

                free(matrix);
                free(labels);

                return EXIT_FAILURE;
            }

            if (matrix[index_of(row, col, cols)] != 0 &&
                matrix[index_of(row, col, cols)] != 1) {

                fprintf(stderr, "A matriz deve conter apenas 0 e 1.\n");

                free(matrix);
                free(labels);

                return EXIT_FAILURE;
            }
        }
    }

    /*
     * Cada thread pode, no pior caso, encontrar uma região
     * diferente em cada célula da sua faixa.
     *
     * rows * cols + 1 é um limite seguro para IDs locais.
     */
    max_local_labels = rows * cols + 1;

    /*
     * Reservamos espaço suficiente para que cada thread
     * tenha um intervalo exclusivo de IDs.
     */
    max_labels =
        num_threads * max_local_labels + 1;

    threads = (pthread_t *) malloc(
        (size_t)num_threads * sizeof(pthread_t)
    );

    thread_data = (ThreadData *) malloc(
        (size_t)num_threads * sizeof(ThreadData)
    );

    uf.parent = (int *) malloc(
        (size_t)max_labels * sizeof(int)
    );

    uf.rank = (int *) calloc(
        (size_t)max_labels,
        sizeof(int)
    );

    uf.size = max_labels;

    if (threads == NULL ||
        thread_data == NULL ||
        uf.parent == NULL ||
        uf.rank == NULL) {

        fprintf(stderr, "Erro ao alocar estruturas paralelas.\n");

        free(matrix);
        free(labels);
        free(threads);
        free(thread_data);
        free(uf.parent);
        free(uf.rank);

        return EXIT_FAILURE;
    }

    for (i = 0; i < max_labels; i++) {
        uf.parent[i] = i;
    }

    /*
     * Divisão das linhas.
     *
     * Se rows não for divisível pelo número de threads,
     * as primeiras threads recebem uma linha adicional.
     */
    base_rows = rows / num_threads;
    extra_rows = rows % num_threads;

    start_row = 0;

    for (i = 0; i < num_threads; i++) {
        int thread_rows;

        thread_rows = base_rows;

        if (i < extra_rows) {
            thread_rows++;
        }

        end_row = start_row + thread_rows;

        thread_data[i].matrix = matrix;
        thread_data[i].labels = labels;
        thread_data[i].rows = rows;
        thread_data[i].cols = cols;
        thread_data[i].thread_id = i;
        thread_data[i].start_row = start_row;
        thread_data[i].end_row = end_row;
        thread_data[i].max_local_labels = max_local_labels;

        if (pthread_create(
                &threads[i],
                NULL,
                worker,
                &thread_data[i]
            ) != 0) {

            fprintf(
                stderr,
                "Erro ao criar thread %d.\n",
                i
            );

            /*
             * Espera as threads que já foram criadas.
             */
            for (i = i - 1; i >= 0; i--) {
                pthread_join(threads[i], NULL);
            }

            free(matrix);
            free(labels);
            free(threads);
            free(thread_data);
            free(uf.parent);
            free(uf.rank);

            return EXIT_FAILURE;
        }

        start_row = end_row;
    }

    /*
     * pthread_join funciona como sincronização:
     * somente depois que todas as threads terminarem
     * começamos a consolidação.
     */
    for (i = 0; i < num_threads; i++) {
        if (pthread_join(threads[i], NULL) != 0) {
            fprintf(
                stderr,
                "Erro ao esperar thread %d.\n",
                i
            );

            free(matrix);
            free(labels);
            free(threads);
            free(thread_data);
            free(uf.parent);
            free(uf.rank);

            return EXIT_FAILURE;
        }
    }

    /*
     * Consolidação.
     *
     * Se temos N faixas, existem N-1 fronteiras.
     */
    for (i = 0; i < num_threads - 1; i++) {
        start_row = 0;

        /*
         * Descobre a última linha da faixa i.
         */
        for (row = 0; row <= i; row++) {
            start_row +=
                base_rows +
                (row < extra_rows ? 1 : 0);
        }

        /*
         * start_row é a primeira linha da próxima faixa.
         * Logo, start_row - 1 é a última linha da faixa atual.
         */
        consolidate_boundary(
            labels,
            cols,
            start_row - 1,
            &uf
        );
    }

    result = count_components(
        matrix,
        labels,
        rows,
        cols,
        &uf,
        max_labels
    );

    if (result < 0) {
        free(matrix);
        free(labels);
        free(threads);
        free(thread_data);
        free(uf.parent);
        free(uf.rank);

        return EXIT_FAILURE;
    }

    printf("Objetos: %d\n", result);
    printf("Threads: %d\n", num_threads);

    free(matrix);
    free(labels);
    free(threads);
    free(thread_data);
    free(uf.parent);
    free(uf.rank);

    return EXIT_SUCCESS;
}
