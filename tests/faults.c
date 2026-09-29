/* Injecao de falhas para validar os caminhos de erro, sem alterar a solucao. */
#include <stddef.h>
#include <sys/types.h>
#include <unistd.h>
#include <errno.h>
#ifdef FAIL_MEMORY
static pid_t original = 0;
void *__real_malloc(size_t size);
void *__wrap_malloc(size_t size)
{
    if (original == 0) original = getpid();
    if (getpid() != original) { errno = ENOMEM; return NULL; }
    return __real_malloc(size);
}
#endif
#ifdef FAIL_FORK
static int calls = 0;
pid_t __real_fork(void);
pid_t __wrap_fork(void)
{
    if (calls++ != 0) { errno = EAGAIN; return -1; }
    return __real_fork();
}
#endif
