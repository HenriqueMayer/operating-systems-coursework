#define _POSIX_C_SOURCE 200809L
#include "matrix.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <errno.h>
#include <limits.h>

typedef struct {
    pid_t pid;
    int reader;
} Worker;

/* Pipes podem transferir menos bytes que o solicitado. */
static int transfer(int fd, void *buffer, size_t bytes, int writing)
{
    unsigned char *p;
    ssize_t moved;
    size_t chunk;
    p = (unsigned char *)buffer;
    while (bytes) {
        chunk = bytes > (size_t)SSIZE_MAX ? (size_t)SSIZE_MAX : bytes;
        moved = writing ? write(fd, p, chunk) : read(fd, p, chunk);
        if (moved < 0 && errno == EINTR) continue;
        if (moved <= 0) return -1;
        p += moved;
        bytes -= (size_t)moved;
    }
    return 0;
}

static int close_pipe(int fd)
{
    /* Nao repetir close apos EINTR: o descritor pode ja estar fechado. */
    if (close(fd) == 0) return 0;
    perror("close pipe");
    return -1;
}

static int child_result(const Matrix *matrix, size_t start, size_t end, int fd)
{
    size_t cells;
    size_t *labels;
    size_t objects;
    int result;
    cells = (end - start) * matrix->cols;
    labels = (size_t *)calloc(cells, sizeof(size_t));
    if (labels == NULL) { perror("calloc rotulos filho"); return -1; }
    result = get_part_objects(matrix, start, end, labels, &objects);
    if (result == 0 &&
        (transfer(fd, &objects, sizeof(objects), 1) != 0 ||
         transfer(fd, labels, matrix->cols * sizeof(size_t), 1) != 0 ||
         transfer(fd, labels + cells - matrix->cols,
                  matrix->cols * sizeof(size_t), 1) != 0)) {
        fprintf(stderr, "Erro ao enviar resultado do filho.\n");
        result = -1;
    }
    free(labels);
    return result;
}

static size_t get_root(size_t *parents, size_t label)
{
    while (parents[label] != label) {
        parents[label] = parents[parents[label]];
        label = parents[label];
    }
    return label;
}

static void merge_boundary(size_t *parents, unsigned char *rank,
                           size_t *upper, size_t *lower, size_t cols,
                           size_t *objects)
{
    size_t col;
    size_t nc;
    size_t first;
    size_t last;
    size_t a;
    size_t b;
    size_t swap;
    for (col = 0; col < cols; col++) {
        if (!upper[col]) continue;
        first = col == 0 ? 0 : col - 1;
        last = col + 1 < cols ? col + 1 : col;
        for (nc = first; nc <= last; nc++) {
            if (!lower[nc]) continue;
            a = get_root(parents, upper[col]);
            b = get_root(parents, lower[nc]);
            if (a == b) continue;
            if (rank[a] < rank[b]) { swap = a; a = b; b = swap; }
            parents[b] = a;
            if (rank[a] == rank[b]) rank[a]++;
            (*objects)--;
        }
    }
}

int main(int argc, char **argv)
{
    Matrix matrix;
    const char *path;
    size_t processes;
    Worker *workers;
    size_t *parents;
    unsigned char *rank;
    size_t *upper;
    size_t *lower;
    size_t *last;
    size_t base;
    size_t extra;
    size_t start;
    size_t end;
    size_t count;
    size_t objects;
    size_t i;
    size_t j;
    size_t created;
    int pipes[2];
    int status;
    int failed;
    int child_failed;
    pid_t pid;
    pid_t waited;
    if (argc > 3) {
        fprintf(stderr, "Uso: %s [arquivo] [processos]\n", argv[0]);
        return EXIT_FAILURE;
    }
    path = argc >= 2 ? argv[1] : "tests/matrizes/exemplo1.txt";
    processes = 2;
    if (argc == 3 && get_processes(argv[2], &processes) != 0) {
        fprintf(stderr, "Quantidade de processos invalida.\n");
        return EXIT_FAILURE;
    }
    if (get_matrix(path, &matrix) != 0) return EXIT_FAILURE;
    if (processes > matrix.rows) processes = matrix.rows;
    /* +1 reserva o rotulo zero, que representa o fundo. */
    if (matrix.cells + 1 > ((size_t)-1) / sizeof(size_t) ||
        processes > ((size_t)-1) / sizeof(Worker)) {
        fprintf(stderr, "Estruturas excedem o limite de tamanho.\n");
        free(matrix.values);
        return EXIT_FAILURE;
    }
    workers = (Worker *)calloc(processes, sizeof(Worker));
    parents = (size_t *)malloc((matrix.cells + 1) * sizeof(size_t));
    rank = (unsigned char *)calloc(matrix.cells + 1, 1);
    upper = (size_t *)malloc(matrix.cols * sizeof(size_t));
    lower = (size_t *)malloc(matrix.cols * sizeof(size_t));
    last = (size_t *)malloc(matrix.cols * sizeof(size_t));
    failed = workers == NULL || parents == NULL || rank == NULL ||
             upper == NULL || lower == NULL || last == NULL;
    created = 0;
    objects = 0;
    if (failed) { perror("alocacao estruturas"); goto cleanup; }
    for (i = 0; i <= matrix.cells; i++) parents[i] = i;
    base = matrix.rows / processes;
    extra = matrix.rows % processes;
    start = 0;
    for (i = 0; i < processes; i++) {
        end = start + base + (i < extra);
        if (pipe(pipes) != 0) { perror("pipe"); failed = 1; break; }
        pid = fork();
        if (pid < 0) {
            perror("fork");
            close_pipe(pipes[0]);
            close_pipe(pipes[1]);
            failed = 1;
            break;
        }
        if (pid == 0) {
            child_failed = close_pipe(pipes[0]) != 0;
            for (j = 0; j < created; j++) {
                if (close_pipe(workers[j].reader) != 0) child_failed = 1;
            }
            if (!child_failed && child_result(&matrix, start, end, pipes[1]) != 0)
                child_failed = 1;
            if (close_pipe(pipes[1]) != 0) child_failed = 1;
            /* _exit evita repetir buffers de stdio herdados pelo fork. */
            _exit(child_failed ? EXIT_FAILURE : EXIT_SUCCESS);
        }
        workers[i].pid = pid;
        workers[i].reader = pipes[0];
        created++;
        if (close_pipe(pipes[1]) != 0) { failed = 1; break; }
        start = end;
    }
    for (i = 0; i < created && !failed; i++) {
        if (transfer(workers[i].reader, &count, sizeof(count), 0) != 0 ||
            transfer(workers[i].reader, lower, matrix.cols * sizeof(size_t), 0) != 0 ||
            transfer(workers[i].reader, last, matrix.cols * sizeof(size_t), 0) != 0) {
            fprintf(stderr, "Resultado incompleto do processo filho.\n");
            failed = 1;
            break;
        }
        objects += count;
        if (i > 0) merge_boundary(parents, rank, upper, lower, matrix.cols, &objects);
        for (j = 0; j < matrix.cols; j++) upper[j] = last[j];
    }
    /* Fechar leitores desbloqueia escritores mesmo em caminhos de erro. */
    for (i = 0; i < created; i++) {
        if (close_pipe(workers[i].reader) != 0) failed = 1;
    }
    for (i = 0; i < created; i++) {
        do { waited = waitpid(workers[i].pid, &status, 0); }
        while (waited < 0 && errno == EINTR);
        if (waited < 0) { perror("waitpid"); failed = 1; }
        else if (!WIFEXITED(status) || WEXITSTATUS(status) != EXIT_SUCCESS) {
            fprintf(stderr, "Processo filho terminou com erro.\n");
            failed = 1;
        }
    }
cleanup:
    free(workers);
    free(parents);
    free(rank);
    free(upper);
    free(lower);
    free(last);
    free(matrix.values);
    if (failed) return EXIT_FAILURE;
    printf("%lu\n", (unsigned long)objects);
    return EXIT_SUCCESS;
}
