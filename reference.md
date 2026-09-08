# Material de apoio - Processos e threads no Linux e macOS

Fonte: [Processos e Threads em Sistemas Operacionais - PDF original](PDF/%5BSisOp%5D_Processos_e_Threads_em_Sistemas_Operacionais_POSIX.pdf), 21 slides. Enunciado do trabalho: [README.md](README.md).

> **Nota de extração:** transcrição na ordem dos slides, com títulos, textos, tabelas, exemplos e referências do material original. Cada número de slide corresponde à página de mesmo número no PDF. Os códigos e as saídas de terminal foram conferidos visualmente; não foram executados nem corrigidos. As afirmações e os resultados apresentados pertencem à fonte. O texto das figuras foi transcrito em subseções identificadas, mantendo os rótulos em inglês. Notas de extração distinguem observações editoriais do conteúdo original; o PDF preserva a apresentação gráfica das figuras.

## Slide 1 - Sistemas Operacionais

**PROCESSOS E THREADS NO LINUX E MACOS**

PUCRS - Escola Politécnica\
Bacharelado em Ciência da Computação\
Prof. Filipo Novo Mór

## Slide 2 - Agenda da aula

### Bloco 1: Processos

- Conceito e Memória
- O PCB (Process Control Block)
- Criação via syscall `fork()`

### Bloco 2: Threads

- Modelo Lightweight Process
- O padrão POSIX (pthreads)
- Comunicação e Mutex

## Slide 3 - 01. Processos

A unidade fundamental de isolamento

## Slide 4 - Definição de processo

Um processo é um **programa em execução**. Diferente do código estático em disco, ele é uma entidade dinâmica.

**Composição:**

- **Código (Text):** Instruções binárias.
- **Dados:** Variáveis globais e estáticas.
- **Pilha (Stack):** Funções e variáveis locais.
- **Heap:** Memória alocada dinamicamente.

### Texto da figura

| Área ou elemento | Rótulos exibidos |
| --- | --- |
| User-space | Local variables; Global variables; Dynamically allocated memory; Code + Constants |
| Kernel-space / Task List | Process 1234; Process 1235 |
| Sinal dirigido a Process 1234 | SIGCHLD |
| PCB | PID: 1235; Running time; Array of opened files; Pointer of parent process |

Anotações numeradas na figura:

1. process 1235 calls exit()
2. kernel frees all the allocated memory
3. kernel frees everything on the user-space memory
4. kernel notifies process 1234 about the termination of its child

## Slide 5 - Criação: syscall fork()

### O Mecanismo

No Linux/macOS, processos são criados clonando um processo pai. O filho herda uma cópia do espaço de memória.

### O Retorno

- **Para o Pai:** Retorna o PID do filho.
- **Para o Filho:** Retorna 0.
- **Erro:** Retorna -1.

## Slide 6 - Exemplo C: fork()

```c
#include
#include

int main() {
  pid_t pid = fork();

  if (pid == 0) {
    printf("Filho executando\n");
  } else {
    printf("Pai criou o processo %d\n", pid);
  }
  return 0;
}
```

> **Nota de extração:** as duas linhas `#include` aparecem sem nomes de cabeçalhos no próprio PDF. Essa lacuna foi preservada, sem completar o exemplo.

## Slide 7 - Traçado de execução: fork()

### Fluxo de Memória

No momento do fork(), o SO duplica o processo. Agora existem dois **Program Counters** apontando para a próxima linha.

### Terminal Output

```text
$ gcc programa.c -o exec
$ ./exec
Pai criou o processo 4502
Filho executando
```

### Texto da figura

Rótulos da figura de memória, de cima para baixo, com as setas exibidas:

```text
Stack
  ↓
Heap
  ↑
Data
Text
```

## Slide 8 - 02. Threads

Concorrência dentro do mesmo espaço

## Slide 9 - Conceito de thread

### "Lightweight Process"

Uma thread é um fluxo de execução dentro de um processo. Enquanto processos são isolados, threads **compartilham** a mesma memória.

### O que é compartilhado?

- Segmento de Código e Dados (Globais).
- Arquivos abertos e Sinais.
- **Privado:** Cada thread tem seu Stack e Registradores.

## Slide 10 - Criação: Pthreads

No Linux e macOS, usamos a biblioteca **POSIX Threads**. A criação não duplica o processo, apenas inicia uma nova função paralelamente.

```c
pthread_create(&thread_id, NULL, funcao, NULL);
```

Diferente de processos, threads exigem que o processo principal espere por elas (pthread_join).

## Slide 11 - Exemplo C: Pthreads

```c
void* print_msg(void* ptr) {
  printf("Executando na Thread!\n");
  return NULL;
}

int main() {
  pthread_t thread;
  pthread_create(&thread, NULL, print_msg, NULL);
  pthread_join(thread, NULL); // Espera a thread
  printf("Main finalizado\n");
  return 0;
}
```

## Slide 12 - Traçado de execução: thread

### Observação Crucial

Se o main terminar sem o pthread_join, o processo morre e todas as threads são encerradas abruptamente.

### Terminal Output

```text
$ gcc t.c -lpthread -o exec
$ ./exec
Executando na Thread!
Main finalizado
```

**Custo:** Criar uma thread é até 100x mais rápido que um processo, pois não há alocação de nova tabela de páginas de memória.

## Slide 13 - Processo vs. thread

| Característica | Processo | Thread |
| --- | --- | --- |
| Memória | Isolada (Privada) | Compartilhada (Mesmo Processo) |
| Troca de Contexto | Alta (Custo do SO) | Baixa (Leve) |
| Falhas | Isoladas (Um não afeta outro) | Críticas (Um erro derruba todas) |
| Comunicação | Difícil (IPC via Kernel) | Fácil (Variáveis Globais) |

## Slide 14 - IPC: Inter-Process Communication

Como processos não acessam a memória uns dos outros, o Kernel atua como mediador através de **IPC**.

| Recurso | Descrição |
| --- | --- |
| Pipes | Fluxo unidirecional de bytes. |
| Shared Mem | Área de memória mapeada em ambos. |
| Messages | Fila de mensagens via Kernel. |

## Slide 15 - Exemplo IPC: pipes

```c
int fd[2]; pipe(fd);
if (fork() == 0) {
  write(fd[1], "OLA", 3);
} else {
  read(fd[0], buf, 3);
  printf("Recebido: %s\n", buf);
}
```

### Terminal Output

```text
Recebido: OLA
```

### Texto da figura - 5 Inter-Process Communications

Crédito exibido: blog.bytebytego.com.

| Nº | Título | Rótulos e conexões exibidos |
| --- | --- | --- |
| 1 | Pipe | write → pipe → read |
| 2 | Message Queue | Process A → fila → Process B |
| 3 | Signal | Process A; Process B; Kernel; SIGINT; Ctrl+C; File Size Limit Exceeded. Setas de Ctrl+C e File Size Limit Exceeded para Kernel; de Kernel para Process A e Process B. |
| 4 | Semaphore | Process A; Process B; acquire; release; Shared Resources; #0, #1, #2, #3, #4. Setas acquire dos processos aos recursos; setas release dos recursos aos processos. |
| 5 | Shared Memory | Process A e Process B, cada um com stack, heap, data e shared memory (mapped), conectados à área shared memory. |

Comando exibido no quadro **Pipe** da figura:

```sh
ps -ef
  | grep 'error'
    | awk '{print $3}'
      | xargs kill -9
```

> **Nota de extração:** as quebras e a disposição do comando acima reproduzem a figura. O comando não foi executado.

## Slide 16 - ITC: Inter-Thread Communication

Threads conversam via variáveis globais. **Problema:** Condições de Corrida (Race Conditions).

### O Perigo

Se duas threads somarem 1 em x = 0 simultaneamente, o resultado pode ser 1 em vez de 2, devido à intercalação das instruções da CPU.

## Slide 17 - A solução: Mutex

O **Mutex** (Mutual Exclusion) garante que apenas uma thread entre na "Região Crítica" por vez.

```c
pthread_mutex_lock(&m);
saldo = saldo + 100;
pthread_mutex_unlock(&m);
```

### Texto da figura

Participantes, da esquerda para a direita: **Thread A**, **Mutex**, **Thread B**. Setas de Thread A para Mutex com os rótulos **Lock** e **unlock**.

Anotações numeradas na figura:

1. Thread A locks mutex and does work with shared resource
2. Thread B attempts to lock mutex and blocks
3. Thread A unlocks mutex
4. Thread B wakes, locks the mutex and does work with the shared resource

## Slide 18 - Rastreio: sincronização

| Sem Mutex | Com Mutex |
| --- | --- |
| Thread 1 lê x=10 | Thread 1 tranca Mutex |
| Thread 2 lê x=10 | Thread 1 lê/escreve x=11 |
| Thread 1 escreve x=11 | Thread 1 destranca Mutex |
| Thread 2 escreve x=11 | Thread 2 tranca... escreve x=12 |
| **Resultado Errado: 11** | **Resultado Correto: 12** |

## Slide 19 - Resumo final

### Processos

Segurança máxima, isolamento, custo alto, comunicação via Kernel.

### Threads

Velocidade, compartilhamento, risco de corrupção de dados, comunicação via memória.

> "Use processos para segurança e threads para performance."

## Slide 20 - Dúvidas?

Sistemas Operacionais | Ciência da Computação

Bacharelado em Ciência da Computação\
Prof. Filipo Novo Mór

## Slide 21 - Image Sources

Referências transcritas na ordem apresentada no slide:

1. [Process-Control-Block-Structure.png](https://www.baeldung.com/wp-content/uploads/sites/2/2023/10/Process-Control-Block-Structure.png)\
   Source: [www.baeldung.com](https://www.baeldung.com)
2. [Process_look.png](https://media.geeksforgeeks.org/wp-content/uploads/20251224114920150586/Process_look.png)\
   Source: [www.geeksforgeeks.org](https://www.geeksforgeeks.org)
3. [0234-inter-process-communication.png](https://assets.bytebytego.com/diagrams/0234-inter-process-communication.png)\
   Source: [bytebytego.com](https://bytebytego.com)
4. [Mutex_lock_for_linux.jpg](https://media.geeksforgeeks.org/wp-content/uploads/Mutex_lock_for_linux.jpg)\
   Source: [www.geeksforgeeks.org](https://www.geeksforgeeks.org)

---

[Enunciado do Trabalho 1](README.md) | [Material de apoio original](PDF/%5BSisOp%5D_Processos_e_Threads_em_Sistemas_Operacionais_POSIX.pdf) | [Sistemas Operacionais](../README.md)
