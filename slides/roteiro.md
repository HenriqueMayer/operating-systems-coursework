# Roteiro da dupla — contagem de objetos

Duração prevista: **8 min 50 s**, com 1 min 10 s de margem até o limite de dez minutos. Membro 1: 4 min 30 s. Membro 2: 4 min 20 s. Substituam os nomes genéricos pelos nomes da dupla ao ensaiar.

O enunciado (página 8) exige participação de ambos e domínio de toda a implementação. Dividir as falas não divide a responsabilidade pelo código.

## Preparação

- Abra `slides/apresentacao.html` no navegador. Funciona sem internet e sem servidor.
- Use as setas para navegar, F para tela cheia e R para o roteiro do slide. Os botões funcionam também pelo teclado.
- O roteiro fica oculto por padrão. Não o abra no projetor durante a fala; use este arquivo em outro dispositivo.
- Na raiz do repositório, execute `make` antes da apresentação. Deixe o terminal com os comandos do slide 12 preparados.
- As simulações do HTML são didáticas: não executam C no navegador. Os trechos foram extraídos do código e as saídas foram capturadas dos executáveis.
- O enunciado pede slides em PDF (página 7, item 50). Use a versão PDF fornecida ou Imprimir / PDF no HTML. No PDF, as simulações mostram seu resultado final.

## Divisão e tempo

| Slide | Assunto | Quem fala | Tempo |
| --- | --- | --- | --- |
| 1 | Contagem de objetos em uma matriz binária | Membro 1 | 15 s |
| 2 | O que conta como um objeto | Membro 1 | 35 s |
| 3 | 1. Ler a matriz e iniciar a sequencial | Membro 1 | 40 s |
| 4 | 2. Encontrar um novo componente | Membro 1 | 40 s |
| 5 | 3. Visitar os oito vizinhos | Membro 1 | 45 s |
| 6 | 4. Acompanhar a contagem sequencial | Membro 1 | 40 s |
| 7 | 5. Dividir as linhas entre processos | Membro 2 | 35 s |
| 8 | 6. Criar os filhos e os pipes | Membro 2 | 40 s |
| 9 | 7. Enviar a contagem e as duas bordas | Membro 2 | 35 s |
| 10 | 8. Consolidar os objetos na fronteira | Membro 2 | 55 s |
| 11 | 9. Evitar a contagem duplicada | Membro 2 | 40 s |
| 12 | 10. Executar e comparar as saídas | Membro 1 | 40 s |
| 13 | 11. Comparar o desempenho | Membro 2 | 40 s |
| 14 | 12. Validação e encerramento | Dupla | 30 s |

## Slide 1 — Contagem de objetos em uma matriz binária

**Quem:** Membro 1. **Tempo:** 15 segundos.

**O que dizer**

Nós implementamos duas versões para contar objetos em uma matriz binária. A primeira é sequencial. A segunda divide o cálculo entre processos POSIX. Vou explicar a entrada e a busca; depois, meu colega explica a divisão e a consolidação.

**Como dizer e o que mostrar**

Fale olhando para a turma. Não leia o título inteiro. Aponte para as duas versões e avance.

**Código ou fonte:** Enunciado, páginas 1, 2 e 8.

## Slide 2 — O que conta como um objeto

**Quem:** Membro 1. **Tempo:** 35 segundos.

**O que dizer**

Cada zero é fundo e cada um pertence ao primeiro plano. Um objeto é um grupo de uns conectados. A conexão inclui os lados e os cantos: são os oito vizinhos. Neste exemplo, temos o grupo do canto superior esquerdo, o grupo à direita e a célula de baixo. Por isso, o resultado é três.

**Como dizer e o que mostrar**

Mostre os três grupos na matriz. No desenho dos vizinhos, destaque as diagonais. Não conte células como se fossem objetos.

**Código ou fonte:** Enunciado, página 4, exemplo 1; tests/matrizes/exemplo1.txt.

## Slide 3 — 1. Ler a matriz e iniciar a sequencial

**Quem:** Membro 1. **Tempo:** 40 segundos.

**O que dizer**

O arquivo começa com o número de linhas e colunas. Depois vêm os valores da matriz. get_matrix lê e valida esses dados. calloc cria os rótulos com zero, indicando que nada foi visitado. Na sequencial, chamamos get_part_objects da linha zero até o total de linhas: ou seja, toda a matriz.

**Como dizer e o que mostrar**

Leia apenas os nomes das três chamadas: get_matrix, calloc e get_part_objects. Explique que o segundo limite da faixa não é incluído. Evite ler cada símbolo do código.

**Código ou fonte:** src/sequencial.c:17–26; src/matrix.c:45–88.

## Slide 4 — 2. Encontrar um novo componente

**Quem:** Membro 1. **Tempo:** 40 segundos.

**O que dizer**

O laço percorre as células. Se for fundo ou já tiver rótulo, ele pula. Quando encontra um um ainda não visitado, soma um objeto. O rótulo é o índice global dessa célula mais um. Depois marca a célula e a coloca na pilha. Esse índice também impede que processos diferentes criem rótulos iguais.

**Como dizer e o que mostrar**

Siga as linhas de cima para baixo. Aponte primeiro para continue, depois objects, labels e stack. Diga que o rótulo é um identificador, não a contagem final.

**Código ou fonte:** src/matrix.c:112–119.

## Slide 5 — 3. Visitar os oito vizinhos

**Quem:** Membro 1. **Tempo:** 45 segundos.

**O que dizer**

Enquanto há células na pilha, o código retira a última e examina os oito vizinhos. Os laços de dr e dc representam os deslocamentos de menos um a mais um. Os limites impedem sair da matriz ou da faixa do processo. Um vizinho só entra na pilha se vale um e ainda não tem rótulo. Ele é marcado antes de entrar, evitando colocá-lo várias vezes. A busca é iterativa, então não depende da pilha de chamadas recursivas.

**Como dizer e o que mostrar**

Use a mão para indicar retirar e inserir na pilha. No trecho visível, destaque a condição e a ordem das duas atribuições. Os laços completos estão nas linhas 120–138 para eventual pergunta.

**Código ou fonte:** src/matrix.c:120–138.

## Slide 6 — 4. Acompanhar a contagem sequencial

**Quem:** Membro 1. **Tempo:** 40 segundos.

**O que dizer**

Vamos acompanhar a mesma matriz. A primeira célula cria o rótulo um. Seus vizinhos recebem esse rótulo e formam um único objeto. Depois, a busca encontra o grupo à direita, com rótulo quatorze, e a célula de baixo, com rótulo vinte e um. Os números dos rótulos são diferentes da contagem: o total é três.

**Como dizer e o que mostrar**

Clique duas vezes em Próximo passo para mostrar o primeiro grupo. Em seguida clique Resultado, para não gastar tempo em todos os passos. Passe a palavra: “Agora vamos dividir essa mesma busca entre processos.”

**Código ou fonte:** src/matrix.c:113–139; exemplo 1.

## Slide 7 — 5. Dividir as linhas entre processos

**Quem:** Membro 2. **Tempo:** 35 segundos.

**O que dizer**

A paralela divide a matriz em faixas de linhas. Com seis linhas e dois processos, cada um recebe três. base calcula a quantidade mínima e extra calcula a sobra. Quando a divisão não é exata, as primeiras faixas recebem uma linha a mais. Cada processo faz trabalho real: executa a busca nas células da sua faixa.

**Como dizer e o que mostrar**

Mostre as duas faixas, não fale em blocos quadrados. Explique que as linhas do desenho começam em um, mas os índices no código começam em zero.

**Código ou fonte:** src/paralela.c:158–162; enunciado, páginas 3 e 4.

## Slide 8 — 6. Criar os filhos e os pipes

**Quem:** Membro 2. **Tempo:** 40 segundos.

**O que dizer**

O pai lê a matriz e cria um pipe antes de cada fork. fork cria um processo filho. Cada filho recebe uma cópia do espaço de memória e executa sua faixa. Não usamos memória compartilhada para escrever os rótulos; cada filho escreve nos seus próprios dados. O pipe leva o resultado ao pai. Depois, waitpid verifica se cada filho terminou corretamente. São dois trabalhadores mais o processo pai.

**Como dizer e o que mostrar**

Percorra o desenho de cima para baixo. Explique a volta dos dados pelos pipes. Diga explicitamente que usamos processos, não threads; por isso não há mutex protegendo esses rótulos.

**Código ou fonte:** src/paralela.c:163–187 e 205–212.

## Slide 9 — 7. Enviar a contagem e as duas bordas

**Quem:** Membro 2. **Tempo:** 35 segundos.

**O que dizer**

O filho chama a mesma função de busca da sequencial. Ao terminar, envia três partes: a quantidade de componentes, a primeira linha de rótulos e a última. Não precisa enviar todos os rótulos porque qualquer conexão com outra faixa passa pela borda. transfer repete read ou write até completar a transferência, pois um pipe pode entregar menos bytes que o solicitado.

**Como dizer e o que mostrar**

Mostre as três chamadas de transfer. Não leia os cálculos de ponteiro; explique que a última expressão aponta para a última linha da faixa.

**Código ou fonte:** src/paralela.c:17–31 e 42–61.

## Slide 10 — 8. Consolidar os objetos na fronteira

**Quem:** Membro 2. **Tempo:** 55 segundos.

**O que dizer**

Esse exemplo mostra por que não basta somar. A faixa superior encontra dois componentes e a inferior encontra três: a soma dá cinco. Mas os rótulos dez e vinte e oito são partes do mesmo objeto central. Eles se encontram na fronteira, inclusive por uma diagonal. Ao unir os dois, a contagem cai para quatro. Outros contatos entre as mesmas partes não reduzem a contagem outra vez.

**Como dizer e o que mostrar**

Clique Próxima etapa para mostrar os rótulos e a soma cinco. Clique novamente para mostrar a união e o total quatro. Clique uma terceira vez para explicar o contato repetido. Aponte para as duas células diagonais.

**Código ou fonte:** Enunciado, página 4, exemplo 2; src/paralela.c:84–96.

## Slide 11 — 9. Evitar a contagem duplicada

**Quem:** Membro 2. **Tempo:** 40 segundos.

**O que dizer**

Union-Find mantém grupos de rótulos equivalentes. get_root encontra o representante de cada grupo. Se os dois representantes já são iguais, continue evita repetir a união e a subtração. Se forem diferentes, parents liga os grupos e objects diminui uma unidade. rank ajuda a manter a estrutura pouco profunda; get_root também comprime o caminho. É isso que mantém a contagem correta quando existem vários contatos na borda.

**Como dizer e o que mostrar**

Aponte principalmente para a igualdade dos representantes e para a subtração. Não explique árvores em detalhes. Se perguntarem sobre os vizinhos, mostre que cada célula compara as colunas esquerda, central e direita da próxima faixa.

**Código ou fonte:** src/paralela.c:64–98.

## Slide 12 — 10. Executar e comparar as saídas

**Quem:** Membro 1. **Tempo:** 40 segundos.

**O que dizer**

Depois de compilar com make, executamos as duas versões sobre o mesmo arquivo. No exemplo um, ambas imprimem três. No exemplo dois, a paralela imprime quatro, como vimos na simulação. A tabela mostra que as cinco matrizes obrigatórias também produziram os resultados esperados. A saída é somente o número de objetos.

**Como dizer e o que mostrar**

Mostre as saídas já registradas no slide. Se houver tempo, rode os dois primeiros comandos no terminal previamente aberto. Não compile nem rode a suíte inteira durante a fala; use as saídas do slide como alternativa.

**Código ou fonte:** Saídas capturadas dos executáveis; tests/matrizes/exemplo1–5.txt; results/validacao.md.

## Slide 13 — 11. Comparar o desempenho

**Quem:** Membro 2. **Tempo:** 40 segundos.

**O que dizer**

Para desempenho, usamos a mesma matriz de oitocentas linhas e colunas. Fizemos cinco medições e usamos a mediana do tempo total. A sequencial levou cerca de sessenta e dois milissegundos. Com dois processos, cerca de cinquenta e sete; com quatro, cerca de cinquenta e seis e meio. A aceleração ficou perto de um vírgula um. O ganho foi pequeno porque leitura, criação dos processos, comunicação e consolidação também custam tempo. Não esperamos que toda matriz fique mais rápida.

**Como dizer e o que mostrar**

Leia os valores arredondados. Explique a fórmula em uma frase. Aponte para a observação do tempo total e não apresente os resultados como garantia de escalabilidade.

**Código ou fonte:** results/benchmark.json e results/desempenho.md; medição local de 29/09/2026.

## Slide 14 — 12. Validação e encerramento

**Quem:** Dupla. **Tempo:** 30 segundos.

**O que dizer**

Membro 1: Além das cinco matrizes, validamos setecentas e vinte e três matrizes em três mil oitocentas e treze execuções C, com uma referência independente. Incluímos diagonais e objetos grandes.

Membro 2: Também verificamos entradas inválidas e falhas de memória e fork. A solução distribui a busca entre os filhos e consolida no pai. As duas versões contam os mesmos objetos nos casos testados.

**Como dizer e o que mostrar**

Cada membro fala por aproximadamente quinze segundos. Termine depois da última frase e deixe espaço para perguntas. Não acrescente slogans nem repita toda a apresentação.

**Código ou fonte:** results/validacao.md; tests/validate.py; enunciado, páginas 8 e 9.

## Demonstração no terminal

Execute a partir da raiz do repositório:

```sh
make
./build/sequencial tests/matrizes/exemplo1.txt
./build/paralela tests/matrizes/exemplo1.txt 2
./build/paralela tests/matrizes/exemplo2.txt 2
```

Saídas esperadas, na ordem: `3`, `3`, `4`. Se a demonstração atrasar, use as saídas capturadas no slide 12. Para mudar a quantidade de trabalhadores, troque o último argumento por `4`. A contagem deve continuar igual.

## Respostas curtas para perguntas

| Pergunta | Resposta |
| --- | --- |
| Por que oito vizinhos? | O enunciado considera conexão por lados e cantos. |
| Por que não basta somar as faixas? | O mesmo objeto pode aparecer em duas faixas e ser contado duas vezes. |
| Por que os rótulos não são 1, 2, 3? | Cada ID usa o índice global da célula inicial mais um; isso garante exclusividade. |
| Usa processos ou threads? | Processos POSIX criados com fork. Não há Pthreads nesta solução. |
| Precisa de mutex? | Não para os rótulos desta arquitetura: os filhos têm memória privada e o pai faz as uniões. |
| Como funciona a conexão diagonal na fronteira? | Cada célula compara as colunas à esquerda, ao centro e à direita na faixa seguinte. |
| Por que enviar só as bordas? | Conexões entre faixas só podem passar pela primeira ou última linha. |
| O que garante que os filhos terminaram bem? | O pai verifica o retorno de waitpid e o status de saída. Se houver erro, não imprime contagem. |
| Por que a busca não é recursiva? | Uma pilha no heap evita estourar a pilha de chamadas em objetos grandes. |
| Por que a aceleração não é duas ou quatro vezes? | Só a busca local é paralela; leitura, coordenação, comunicação e consolidação têm custo. |
| Foi validado em macOS? | Não. Esta validação e estas medições foram feitas em Linux. |
| O que acontece com mais processos que linhas? | A quantidade de trabalhadores é limitada ao número de linhas. |

## Ensaio

Façam um ensaio com cronômetro e as mesmas ações dos slides 6 e 10. Se passar de nove minutos, reduzam explicações de rank e detalhes de ponteiro, mantendo a conexão diagonal, a união sem duplicação e os resultados. Cada membro deve conseguir explicar a parte do colega.

## Fontes e atualização

Enunciado original, páginas 1–9; código em `src/`; matrizes em `tests/matrizes/`; resultados em `results/`. A logo foi extraída do próprio PDF do enunciado, sem redesenho. As capturas do código incluem arquivo e linhas. Se o código ou os resultados mudarem, regenere o HTML com `python3 slides/scripts/build.py` e as capturas/PDF com o script de renderização.
