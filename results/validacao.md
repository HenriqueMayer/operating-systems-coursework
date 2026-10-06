# Validação da solução C

Validação executada em 29/09/2026, em Linux. Compilação C89/C90 com `-Wall -Wextra -pedantic -Werror`, sem avisos.

- 723 matrizes: cinco obrigatórias, todas as 512 matrizes binárias 3 × 3, 200 aleatórias com semente fixa e seis casos adicionais.
- 3.813 execuções C comparadas com uma busca independente, sem divergências.
- Contagens obrigatórias: 3, 4, 5, 6 e 7 nas duas versões.
- Verificados primeiro plano vazio, matriz cheia, objetos isolados, coluna única, diagonais entre faixas, divisões desiguais e pedidos de processos superiores ao número de linhas.
- Uma linha com 200.000 células conectadas e uma matriz cheia 200 × 200 foram processadas sem recursão.
- Entradas vazias, dimensões inválidas ou excessivas, matrizes incompletas, valores não binários, dados excedentes, arquivos ausentes e argumentos de processos inválidos foram rejeitados.
- Falha de alocação da pilha nos filhos e falha de fork após criar o primeiro filho foram simuladas: encerramento com erro, sem publicar contagem parcial.
- A mesma suíte passou com AddressSanitizer e UndefinedBehaviorSanitizer, sem diagnósticos nos casos válidos.

Comandos: `make test` e `make sanitize`. Os testes de falha são compilados separadamente, sem sanitizadores, usando o linker GNU em Linux. Os testes não simulam todas as falhas possíveis das APIs POSIX e não comprovam ausência de erros para qualquer tamanho de entrada.

O código C usa APIs disponíveis em Linux e macOS; esta execução não validou uma máquina macOS.

## Revalidação para entrega — 06/10/2026

A compilação com `-O2 -std=c89 -Wall -Wextra -pedantic -Werror` terminou sem avisos. `make test` e `make sanitize` passaram novamente: 723 matrizes, 3.813 execuções C, entradas inválidas e falhas simuladas verificadas. Não houve divergências nem diagnósticos dos sanitizadores. Os binários foram recompilados sem instrumentação após os testes; os resultados de desempenho de 29/09/2026 não foram refeitos.
