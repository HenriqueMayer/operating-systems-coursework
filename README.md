# Contagem de objetos em matrizes binárias

Trabalho de Sistemas Operacionais — PUCRS, 2026/II. Implementações em C89/C90 que contam regiões de células `1` conectadas pelos oito vizinhos, incluindo diagonais.

Os contribuidores registrados no histórico do repositório são Henrique Ramos Mayer e Eduardo Santos. O enunciado e o material de apoio são do professor Filipo Mór. A conversão, organização e validação desta versão tiveram assistência do Codex.

## Compilação e execução

Requisitos: Linux ou macOS, compilador C e Make. Python 3 é usado nos scripts de teste e nas referências, sem bibliotecas adicionais.

```sh
make
./build/sequencial tests/matrizes/exemplo1.txt
./build/paralela tests/matrizes/exemplo1.txt 2
```

Ambos imprimem apenas a quantidade de objetos; no exemplo acima, `3`. Sem argumentos, usam `tests/matrizes/exemplo1.txt`, relativo ao diretório atual. A paralela usa dois processos trabalhadores por padrão e limita a quantidade ao número de linhas. Para execução efetivamente paralela, use pelo menos dois trabalhadores em uma matriz com pelo menos duas linhas. O processo pai coordena os trabalhadores.

O arquivo começa com `linhas colunas`, seguido de exatamente essa quantidade de valores binários separados por espaços ou quebras de linha:

```text
2 2
1 0
0 1
```

Esse exemplo tem um objeto pela conexão diagonal. Dimensões não positivas, valores diferentes de `0` e `1`, entrada incompleta ou excedente e quantidades inválidas de processos são rejeitados. Falhas de entrada, memória ou processos retornam código diferente de zero e escrevem o diagnóstico em stderr.

## Organização

```text
src/                 Código C e funções comuns de entrada e flood fill
reference/python/    Versões Python preservadas como referência
tests/matrizes/      Cinco matrizes obrigatórias
tests/validate.py    Comparação independente e regressões
tests/faults.c       Simulação de falhas em Linux
tests/benchmark.py  Medições reproduzíveis
docs/enunciado.md    Transcrição do enunciado
docs/reference.md   Transcrição do material de apoio
PDF/                PDFs originais e extração em PDF/extracao/
results/            Resultados de desempenho e validação
build/              Executáveis gerados, ignorados pelo Git
```

Os executáveis antigos da raiz foram retirados da árvore versionada. As fontes C anteriores foram substituídas pelas conversões organizadas em `src/`; seu histórico permanece no Git. O antigo `teste.txt` corresponde a `tests/matrizes/exemplo1.txt`.

## Algoritmos

A sequencial percorre a matriz, inicia um flood fill para cada célula de primeiro plano ainda não rotulada e marca seus oito vizinhos. A busca usa uma pilha alocada no heap, evitando o limite de recursão das referências Python e da versão C anterior.

A paralela acompanha a estratégia da referência Python: divide as linhas em faixas equilibradas e usa processos POSIX (`fork`). Cada filho rotula seus componentes localmente e envia por pipe a contagem e os rótulos da primeira e última linha. O ID de um componente é o índice global de sua célula inicial mais um, garantindo exclusividade entre faixas.

O pai soma as contagens e compara cada célula da borda superior com as três possíveis vizinhas da faixa inferior. Union-Find com compressão de caminhos e união por rank reúne componentes equivalentes; cada união nova reduz a contagem em um. União repetida não reduz novamente o resultado.

Os filhos não alteram memória compartilhada: a memória herdada por `fork` é privada. Pipes fazem a comunicação, e `waitpid` verifica o encerramento de todos os filhos. A rotulação das faixas é paralela; leitura da entrada, consolidação e coordenação permanecem sequenciais. A estratégia usa faixas, portanto não há divisões verticais em colunas; as conexões dentro de cada faixa são tratadas pelo flood fill.

A versão sequencial utiliza tempo e memória O(linhas × colunas). Na paralela, cada filho aloca rótulos e pilha proporcionais à sua faixa; o pai mantém Union-Find proporcional ao total de células e recebe duas linhas por trabalhador. Criação de processos, leitura e consolidação podem limitar a aceleração.

## Validação e desempenho

```sh
make test
make sanitize
make clean
make
make benchmark
```

`make test` verifica as cinco matrizes obrigatórias, todas as 512 matrizes binárias 3 × 3, 200 matrizes aleatórias e casos grandes e de fronteira. Compara as duas versões com uma busca independente, variando trabalhadores, incluindo divisões desiguais e solicitações maiores que o número de linhas. Também verifica entradas inválidas e falhas simuladas de alocação no filho e de `fork`; a simulação requer linker GNU em Linux.

`make sanitize` recompila com AddressSanitizer e UndefinedBehaviorSanitizer. Os binários permanecem instrumentados ao terminar; execute `make clean && make` antes das medições de desempenho.

| Exemplo | Dimensões | Esperado | Sequencial | Paralela |
| --- | --- | ---: | ---: | ---: |
| 1 | 5 × 5 | 3 | 3 | 3 |
| 2 | 6 × 8 | 4 | 4 | 4 |
| 3 | 8 × 8 | 5 | 5 | 5 |
| 4 | 9 × 12 | 6 | 6 | 6 |
| 5 | 12 × 12 | 7 | 7 | 7 |

Resultados: [validação](results/validacao.md) e [desempenho](results/desempenho.md). As medições usam os mesmos dados, cinco repetições e a mediana do tempo total. Os resultados representam este ambiente; não garantem aceleração em outras matrizes ou máquinas.

As referências Python podem ser executadas a partir da raiz:

```sh
python3 reference/python/sequencial.py
python3 reference/python/paralela.py
```

A sequencial Python foi preservada com suas limitações: recursão em objetos grandes e ausência de validação da entrada. A versão C corrige essas limitações. Slides de apresentação ainda não foram produzidos.

## Fontes

- [Enunciado do trabalho](docs/enunciado.md)
- [Material de apoio sobre processos e threads](docs/reference.md)
- [Relatório da extração dos PDFs](PDF/extracao/relatorio.md)

Não há dependências externas no código C além da biblioteca padrão e das APIs POSIX.
