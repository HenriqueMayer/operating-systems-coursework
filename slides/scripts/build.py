"""Gera HTML autocontido e roteiro a partir do codigo e resultados locais."""
from pathlib import Path
import base64,html,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'slides'
def number(value):return f'{value:.2f}'.replace('.',',')
def enc(p):return 'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode()
def snippet(file,start,end):
 lines=(ROOT/file).read_text().splitlines()
 text='\n'.join(f'{i:>3}  {lines[i-1]}' for i in range(start,end+1))
 key=f'{Path(file).stem}-{start}-{end}'
 capture=OUT/'assets/codigo'/f'{key}.png'
 if capture.exists() and '--text-code' not in sys.argv:
  alt=html.escape(f'{file}, linhas {start} a {end}. '+text,quote=True)
  return f'<figure class="code" data-code="{key}"><img src="{enc(capture)}" alt="{alt}"></figure>'
 return f'<figure class="code" data-code="{key}"><figcaption>{file} · linhas {start}–{end}</figcaption><pre><code>{html.escape(text)}</code></pre></figure>'
def grid(a,labels=None,split=None,id=None):
 cols=len(a[0]);cells=''
 for r,row in enumerate(a):
  for c,v in enumerate(row):
   label=labels[r][c] if labels else v
   cls='filled' if v else 'zero'
   cells+=f'<span class="cell {cls}" data-value="{v}" data-row="{r}" data-col="{c}">{label}</span>'
 boundary=f'<span class="boundary" style="top:{split/len(a)*100}%" aria-hidden="true"></span>' if split else ''
 return f'<div class="matrix-wrap"><div class="matrix" {f"id={id}" if id else ""} style="--cols:{cols};--rows:{len(a)}" role="img" aria-label="Matriz {len(a)} por {cols}; valores e rótulos descritos no texto">{cells}</div>{boundary}</div>'
def load(i):
 v=list(map(int,(ROOT/f'tests/matrizes/exemplo{i}.txt').read_text().split()));return [v[2+r*v[1]:2+(r+1)*v[1]] for r in range(v[0])]
def trace(a,start=0,end=None):
 end=end or len(a); cols=len(a[0]);labels=[[0]*cols for _ in a];count=0;frames=[]
 for r in range(start,end):
  for c in range(cols):
   if not a[r][c] or labels[r][c]:continue
   count+=1;lab=r*cols+c+1;labels[r][c]=lab;stack=[(r,c)]
   frames.append({'labels':[row[:] for row in labels],'objects':count,'text':f'Novo componente: linha {r+1}, coluna {c+1}. Rótulo {lab}; contagem {count}.','stack':len(stack)})
   while stack:
    rr,cc=stack.pop()
    for dr in (-1,0,1):
     for dc in (-1,0,1):
      nr,nc=rr+dr,cc+dc
      if start<=nr<end and 0<=nc<cols and a[nr][nc] and not labels[nr][nc]:labels[nr][nc]=lab;stack.append((nr,nc))
    frames.append({'labels':[row[:] for row in labels],'objects':count,'text':f'Retira linha {rr+1}, coluna {cc+1} da pilha e verifica os oito vizinhos.','stack':len(stack)})
 if frames:
  frames[-1]['text']=f'Busca encerrada: {count} objetos, todos os componentes rotulados.'
 return labels,count,frames
bench=json.loads((ROOT/'results/benchmark.json').read_text()); a1=load(1);a2=load(2)
l1,count,frames=trace(a1);top,nt,_=trace(a2,0,3);bottom,nb,_=trace(a2,3,6)
local=[[top[r][c] or bottom[r][c] for c in range(8)] for r in range(6)]
merged=[[10 if x==28 else x for x in row] for row in local]
# Captura as saidas diretamente dos executaveis atuais.
outputs=[]
for args in [['build/sequencial','tests/matrizes/exemplo1.txt'],['build/paralela','tests/matrizes/exemplo1.txt','2'],['build/paralela','tests/matrizes/exemplo2.txt','2']]:
 result=subprocess.run([str(ROOT/args[0])]+args[1:],cwd=ROOT,capture_output=True,text=True,check=True)
 outputs.append('$ ./'+ ' '.join(args)+'\n'+result.stdout.strip())
(OUT/'assets/saidas.txt').write_text('\n\n'.join(outputs)+'\n')
slides=[]
def add(title,who,seconds,body,say,how,source):slides.append(dict(title=title,who=who,seconds=seconds,body=body,say=say,how=how,source=source))
add('Contagem de objetos em uma matriz binária','Membro 1',15,
 '<div class="cover"><p class="course">Sistemas Operacionais · PUCRS · 2026/II</p><h1>Contagem de objetos<br>em uma matriz binária</h1><p>Versão sequencial e versão paralela com processos POSIX</p><p class="authors">Apresentação em dupla · C89/C90</p></div>',
 'Nós implementamos duas versões para contar objetos em uma matriz binária. A primeira é sequencial. A segunda divide o cálculo entre processos POSIX. Vou explicar a entrada e a busca; depois, meu colega explica a divisão e a consolidação.',
 'Fale olhando para a turma. Não leia o título inteiro. Aponte para as duas versões e avance.',
 'Enunciado, páginas 1, 2 e 8.')
add('O que conta como um objeto','Membro 1',35,
 f'<div class="columns"><div>{grid(a1)}<p class="caption">Exemplo 1 do enunciado · 5 × 5</p></div><div><p><strong>0</strong> é fundo. <strong>1</strong> pertence a um objeto.</p><p>As células se conectam por lados <strong>ou diagonais</strong>.</p><div class="neighbors"><span>↖</span><span>↑</span><span>↗</span><span>←</span><strong>1</strong><span>→</span><span>↙</span><span>↓</span><span>↘</span></div><p class="result">Resultado: 3 objetos</p></div></div>',
 'Cada zero é fundo e cada um pertence ao primeiro plano. Um objeto é um grupo de uns conectados. A conexão inclui os lados e os cantos: são os oito vizinhos. Neste exemplo, temos o grupo do canto superior esquerdo, o grupo à direita e a célula de baixo. Por isso, o resultado é três.',
 'Mostre os três grupos na matriz. No desenho dos vizinhos, destaque as diagonais. Não conte células como se fossem objetos.',
 'Enunciado, página 4, exemplo 1; tests/matrizes/exemplo1.txt.')
add('1. Ler a matriz e iniciar a sequencial','Membro 1',40,
 '<div class="columns wide-code"><div>'+snippet('src/sequencial.c',17,26)+'</div><div><pre class="input">5 5\n1 1 0 0 0\n1 1 0 0 0\n0 0 0 1 0\n0 0 0 1 0\n1 0 0 0 0</pre><p>Leitura → rótulos zerados → busca</p><p class="small">A entrada é validada antes da contagem.</p></div></div>',
 'O arquivo começa com o número de linhas e colunas. Depois vêm os valores da matriz. get_matrix lê e valida esses dados. calloc cria os rótulos com zero, indicando que nada foi visitado. Na sequencial, chamamos get_part_objects da linha zero até o total de linhas: ou seja, toda a matriz.',
 'Leia apenas os nomes das três chamadas: get_matrix, calloc e get_part_objects. Explique que o segundo limite da faixa não é incluído. Evite ler cada símbolo do código.',
 'src/sequencial.c:17–26; src/matrix.c:45–88.')
add('2. Encontrar um novo componente','Membro 1',40,
 '<div class="columns wide-code"><div>'+snippet('src/matrix.c',112,119)+'</div><div><ol><li>Pular fundo e células já rotuladas.</li><li>Somar um objeto.</li><li>Marcar a célula e colocá-la na pilha.</li></ol><p class="small">Rótulo = índice global da célula inicial + 1.<br>Zero fica reservado para o fundo.</p></div></div>',
 'O laço percorre as células. Se for fundo ou já tiver rótulo, ele pula. Quando encontra um um ainda não visitado, soma um objeto. O rótulo é o índice global dessa célula mais um. Depois marca a célula e a coloca na pilha. Esse índice também impede que processos diferentes criem rótulos iguais.',
 'Siga as linhas de cima para baixo. Aponte primeiro para continue, depois objects, labels e stack. Diga que o rótulo é um identificador, não a contagem final.',
 'src/matrix.c:112–119.')
add('3. Visitar os oito vizinhos','Membro 1',45,
 '<div class="columns wide-code"><div>'+snippet('src/matrix.c',132,135)+'</div><div><p>Enquanto a pilha tiver células:</p><ol><li>Retirar a última célula.</li><li>Verificar os oito vizinhos dentro da faixa.</li><li>Marcar e empilhar os vizinhos com valor 1.</li></ol><p>Marcar <strong>antes</strong> de empilhar evita duplicações.</p><p class="small">A pilha fica no heap; a busca não usa recursão.</p></div></div>',
 'Enquanto há células na pilha, o código retira a última e examina os oito vizinhos. Os laços de dr e dc representam os deslocamentos de menos um a mais um. Os limites impedem sair da matriz ou da faixa do processo. Um vizinho só entra na pilha se vale um e ainda não tem rótulo. Ele é marcado antes de entrar, evitando colocá-lo várias vezes. A busca é iterativa, então não depende da pilha de chamadas recursivas.',
 'Use a mão para indicar retirar e inserir na pilha. No trecho visível, destaque a condição e a ordem das duas atribuições. Os laços completos estão nas linhas 120–138 para eventual pergunta.',
 'src/matrix.c:120–138.')
add('4. Acompanhar a contagem sequencial','Membro 1',40,
 f'<div class="columns"><div>{grid(a1,id="seq-matrix")}<p class="caption">Cada rótulo identifica um componente</p></div><div><p id="seq-text" aria-live="polite">A matriz ainda não foi percorrida.</p><p class="result">Objetos: <span id="seq-count">0</span></p><p>Células na pilha: <span id="seq-stack">0</span></p><div class="sim-controls"><button id="seq-reset">Reiniciar</button><button id="seq-next">Próximo passo</button><button id="seq-end">Resultado</button></div><p class="small">Simulação da ordem de marcação do código C.</p></div></div>',
 'Vamos acompanhar a mesma matriz. A primeira célula cria o rótulo um. Seus vizinhos recebem esse rótulo e formam um único objeto. Depois, a busca encontra o grupo à direita, com rótulo quatorze, e a célula de baixo, com rótulo vinte e um. Os números dos rótulos são diferentes da contagem: o total é três.',
 'Clique duas vezes em Próximo passo para mostrar o primeiro grupo. Em seguida clique Resultado, para não gastar tempo em todos os passos. Passe a palavra: “Agora vamos dividir essa mesma busca entre processos.”',
 'src/matrix.c:113–139; exemplo 1.')
add('5. Dividir as linhas entre processos','Membro 2',35,
 '<div class="columns wide-code"><div>'+snippet('src/paralela.c',158,162)+'</div><div><div class="stripes"><div>Processo 1 · linhas 1 a 3</div><div>Processo 2 · linhas 4 a 6</div></div><p>Exemplo: 6 linhas ÷ 2 processos</p><p class="small">Se houver sobra, os primeiros processos recebem uma linha a mais.</p><p>Dentro da faixa, a busca é a mesma.</p></div></div>',
 'A paralela divide a matriz em faixas de linhas. Com seis linhas e dois processos, cada um recebe três. base calcula a quantidade mínima e extra calcula a sobra. Quando a divisão não é exata, as primeiras faixas recebem uma linha a mais. Cada processo faz trabalho real: executa a busca nas células da sua faixa.',
 'Mostre as duas faixas, não fale em blocos quadrados. Explique que as linhas do desenho começam em um, mas os índices no código começam em zero.',
 'src/paralela.c:158–162; enunciado, páginas 3 e 4.')
add('6. Criar os filhos e os pipes','Membro 2',40,
 '<div class="process-flow"><div class="parent">Pai: matriz e divisão</div><div class="fork-label">fork()</div><div class="children"><div>Filho 1<br><small>busca na faixa superior</small></div><div>Filho 2<br><small>busca na faixa inferior</small></div></div><div class="pipe-label">pipe 1 ↓ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ↓ pipe 2</div><div class="parent">Pai: recebe e consolida</div></div><p class="caption">Memória privada nos filhos · comunicação por pipes · encerramento verificado com waitpid</p>',
 'O pai lê a matriz e cria um pipe antes de cada fork. fork cria um processo filho. Cada filho recebe uma cópia do espaço de memória e executa sua faixa. Não usamos memória compartilhada para escrever os rótulos; cada filho escreve nos seus próprios dados. O pipe leva o resultado ao pai. Depois, waitpid verifica se cada filho terminou corretamente. São dois trabalhadores mais o processo pai.',
 'Percorra o desenho de cima para baixo. Explique a volta dos dados pelos pipes. Diga explicitamente que usamos processos, não threads; por isso não há mutex protegendo esses rótulos.',
 'src/paralela.c:163–187 e 205–212.')
add('7. Enviar a contagem e as duas bordas','Membro 2',35,
 '<div class="columns wide-code"><div>'+snippet('src/paralela.c',51,56)+'</div><div><p>Cada filho envia:</p><ol><li>A quantidade de componentes locais.</li><li>Os rótulos da primeira linha.</li><li>Os rótulos da última linha.</li></ol><p class="small">As células internas já foram resolvidas na busca local.</p></div></div>',
 'O filho chama a mesma função de busca da sequencial. Ao terminar, envia três partes: a quantidade de componentes, a primeira linha de rótulos e a última. Não precisa enviar todos os rótulos porque qualquer conexão com outra faixa passa pela borda. transfer repete read ou write até completar a transferência, pois um pipe pode entregar menos bytes que o solicitado.',
 'Mostre as três chamadas de transfer. Não leia os cálculos de ponteiro; explique que a última expressão aponta para a última linha da faixa.',
 'src/paralela.c:17–31 e 42–61.')
add('8. Consolidar os objetos na fronteira','Membro 2',55,
 f'<div class="columns"><div>{grid(a2,split=3,id="merge-matrix")}<p class="caption">Exemplo 2 · linha laranja separa as faixas</p></div><div><p id="merge-text" aria-live="polite">A matriz inteira tem 4 objetos.</p><p class="result" id="merge-count">Resultado esperado: 4</p><div class="sim-controls"><button id="merge-reset">Reiniciar</button><button id="merge-next">Próxima etapa</button></div><p class="small">Rótulos locais centrais: 10 e 28.<br>Contato diagonal: linha 3, coluna 3 ↔ linha 4, coluna 4.</p></div></div>',
 'Esse exemplo mostra por que não basta somar. A faixa superior encontra dois componentes e a inferior encontra três: a soma dá cinco. Mas os rótulos dez e vinte e oito são partes do mesmo objeto central. Eles se encontram na fronteira, inclusive por uma diagonal. Ao unir os dois, a contagem cai para quatro. Outros contatos entre as mesmas partes não reduzem a contagem outra vez.',
 'Clique Próxima etapa para mostrar os rótulos e a soma cinco. Clique novamente para mostrar a união e o total quatro. Clique uma terceira vez para explicar o contato repetido. Aponte para as duas células diagonais.',
 'Enunciado, página 4, exemplo 2; src/paralela.c:84–96.')
add('9. Evitar a contagem duplicada','Membro 2',40,
 '<div class="columns wide-code"><div>'+snippet('src/paralela.c',89,96)+'</div><div><p>Union-Find guarda quais rótulos pertencem ao mesmo objeto.</p><ol><li>Encontrar os representantes.</li><li>Se já forem iguais, não fazer nada.</li><li>Se forem diferentes, unir e subtrair um.</li></ol><p class="small">O rank orienta a união. get_root encurta os caminhos.</p></div></div>',
 'Union-Find mantém grupos de rótulos equivalentes. get_root encontra o representante de cada grupo. Se os dois representantes já são iguais, continue evita repetir a união e a subtração. Se forem diferentes, parents liga os grupos e objects diminui uma unidade. rank ajuda a manter a estrutura pouco profunda; get_root também comprime o caminho. É isso que mantém a contagem correta quando existem vários contatos na borda.',
 'Aponte principalmente para a igualdade dos representantes e para a subtração. Não explique árvores em detalhes. Se perguntarem sobre os vizinhos, mostre que cada célula compara as colunas esquerda, central e direita da próxima faixa.',
 'src/paralela.c:64–98.')
add('10. Executar e comparar as saídas','Membro 1',40,
 '<div class="columns"><pre class="terminal">'+html.escape('\n\n'.join(outputs))+'</pre><div><table><thead><tr><th>Exemplo</th><th>Esperado</th><th>Seq.</th><th>Par.</th></tr></thead><tbody>'+''.join(f'<tr><td>{i}</td><td>{i+2}</td><td>{i+2}</td><td>{i+2}</td></tr>' for i in range(1,6))+'</tbody></table><p class="small">Cinco matrizes obrigatórias, mesmos resultados.</p></div></div>',
 'Depois de compilar com make, executamos as duas versões sobre o mesmo arquivo. No exemplo um, ambas imprimem três. No exemplo dois, a paralela imprime quatro, como vimos na simulação. A tabela mostra que as cinco matrizes obrigatórias também produziram os resultados esperados. A saída é somente o número de objetos.',
 'Mostre as saídas já registradas no slide. Se houver tempo, rode os dois primeiros comandos no terminal previamente aberto. Não compile nem rode a suíte inteira durante a fala; use as saídas do slide como alternativa.',
 'Saídas capturadas dos executáveis; tests/matrizes/exemplo1–5.txt; results/validacao.md.')
records=bench['records']
rows=''.join(f'<tr><td>{"Sequencial" if r["processes"] is None else str(r["processes"])+" processos"}</td><td>{number(r["median_seconds"]*1000)} ms</td><td>{number(r["speedup"])}×</td></tr>' for r in records)
bars=''.join(f'<div class="bar-row"><span>{"Sequencial" if r["processes"] is None else str(r["processes"])+" processos"}</span><div class="bar-track"><div style="width:{r["median_seconds"]/records[0]["median_seconds"]*100:.2f}%"></div></div><strong>{number(r["median_seconds"]*1000)} ms</strong></div>' for r in records)
add('11. Comparar o desempenho','Membro 2',40,
 '<p>Matriz 800 × 800 · cinco repetições · mediana do tempo total</p><div class="columns"><div class="chart">'+bars+'</div><div><table><thead><tr><th>Versão</th><th>Tempo</th><th>Aceleração</th></tr></thead><tbody>'+rows+'</tbody></table><p class="formula">Aceleração = tempo sequencial ÷ tempo paralelo</p></div></div><p class="small">Medição local em Linux. Inclui leitura, criação dos processos, pipes e consolidação. A paralela pode ser mais lenta em outros casos.</p>',
 'Para desempenho, usamos a mesma matriz de oitocentas linhas e colunas. Fizemos cinco medições e usamos a mediana do tempo total. A sequencial levou cerca de sessenta e dois milissegundos. Com dois processos, cerca de cinquenta e sete; com quatro, cerca de cinquenta e seis e meio. A aceleração ficou perto de um vírgula um. O ganho foi pequeno porque leitura, criação dos processos, comunicação e consolidação também custam tempo. Não esperamos que toda matriz fique mais rápida.',
 'Leia os valores arredondados. Explique a fórmula em uma frase. Aponte para a observação do tempo total e não apresente os resultados como garantia de escalabilidade.',
 'results/benchmark.json e results/desempenho.md; medição local de 29/09/2026.')
add('12. Validação e encerramento','Dupla',30,
 '<div class="columns"><div><h3>Correção</h3><p>723 matrizes · 3.813 execuções C</p><p>Casos obrigatórios, aleatórios, diagonais e objetos grandes.</p><p class="small">Testes também com AddressSanitizer e UndefinedBehaviorSanitizer.</p></div><div><h3>Tratamento de falhas</h3><p>Entrada inválida e falhas simuladas de memória e fork.</p><p>Sem publicar contagem parcial em caso de erro.</p></div></div><p class="closing">A busca local é paralela. A consolidação fica no pai.</p>',
 'Membro 1: Além das cinco matrizes, validamos setecentas e vinte e três matrizes em três mil oitocentas e treze execuções C, com uma referência independente. Incluímos diagonais e objetos grandes.\n\nMembro 2: Também verificamos entradas inválidas e falhas de memória e fork. A solução distribui a busca entre os filhos e consolida no pai. As duas versões contam os mesmos objetos nos casos testados.',
 'Cada membro fala por aproximadamente quinze segundos. Termine depois da última frase e deixe espaço para perguntas. Não acrescente slogans nem repita toda a apresentação.',
 'results/validacao.md; tests/validate.py; enunciado, páginas 8 e 9.')
assert sum(s['seconds'] for s in slides)==530
logo=enc(OUT/'assets/pucrs.png')
sections=[]
for i,s in enumerate(slides,1):
 head='' if i==1 else f'<h2>{s["title"]}</h2>'
 sections.append(f'<section class="slide" id="slide-{i}" aria-label="Slide {i}: {html.escape(s["title"])}"><header><img src="{logo}" alt="Logo da PUCRS"><span>Sistemas Operacionais</span></header>{head}<div class="content">{s["body"]}</div><footer><span>{s["who"]} · {s["seconds"]} s</span><span>{i:02d} / {len(slides):02d}</span></footer></section>')
notes=[{k:s[k] for k in ('title','who','seconds','say','how','source')} for s in slides]
(OUT/'assets/conteudo.json').write_text(json.dumps({'slides':notes,'sequential':frames,'parallel_labels':local,'parallel_merged':merged},ensure_ascii=False,indent=2)+'\n')
css=(OUT/'scripts/style.css').read_text();js=(OUT/'scripts/presentation.js').read_text()
page=f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Contagem de objetos — Sistemas Operacionais PUCRS</title><style>{css}</style></head><body><a class="skip" href="#deck">Ir para apresentação</a><main id="deck">{''.join(sections)}</main><nav class="navigation" aria-label="Controles da apresentação"><button id="prev" aria-label="Slide anterior">←</button><span id="progress" role="status" aria-live="polite">1 / {len(slides)}</span><button id="next" aria-label="Próximo slide">→</button><button id="notes-toggle" aria-expanded="false" aria-controls="notes">Roteiro</button><button id="fullscreen">Tela cheia</button><button id="print">Imprimir / PDF</button><span class="keys">← → slides · R roteiro · F tela cheia</span></nav><aside id="notes" hidden aria-label="Roteiro do slide"><button id="notes-close" aria-label="Fechar roteiro">Fechar</button><h3 id="notes-title"></h3><p id="notes-say"></p><h4>Como apresentar</h4><p id="notes-how"></p><p class="small" id="notes-source"></p></aside><script>const NOTES={json.dumps(notes,ensure_ascii=False)};const FRAMES={json.dumps(frames,ensure_ascii=False)};const LOCAL={json.dumps(local)};const MERGED={json.dumps(merged)};{js}</script></body></html>'''
(OUT/'apresentacao.html').write_text(page)
lines=['# Roteiro da dupla — contagem de objetos','', 'Duração prevista: **8 min 50 s**, com 1 min 10 s de margem até o limite de dez minutos. Membro 1: 4 min 30 s. Membro 2: 4 min 20 s. Substituam os nomes genéricos pelos nomes da dupla ao ensaiar.','', 'O enunciado (página 8) exige participação de ambos e domínio de toda a implementação. Dividir as falas não divide a responsabilidade pelo código.','', '## Preparação', '', '- Abra `slides/apresentacao.html` no navegador. Funciona sem internet e sem servidor.', '- Use as setas para navegar, F para tela cheia e R para o roteiro do slide. Os botões funcionam também pelo teclado.', '- O roteiro fica oculto por padrão. Não o abra no projetor durante a fala; use este arquivo em outro dispositivo.', '- Na raiz do repositório, execute `make` antes da apresentação. Deixe o terminal com os comandos do slide 12 preparados.', '- As simulações do HTML são didáticas: não executam C no navegador. Os trechos foram extraídos do código e as saídas foram capturadas dos executáveis.', '- O enunciado pede slides em PDF (página 7, item 50). Use a versão PDF fornecida ou Imprimir / PDF no HTML. No PDF, as simulações mostram seu resultado final.', '', '## Divisão e tempo', '', '| Slide | Assunto | Quem fala | Tempo |', '| --- | --- | --- | --- |']
for i,s in enumerate(slides,1):lines.append(f'| {i} | {s["title"]} | {s["who"]} | {s["seconds"]} s |')
for i,s in enumerate(slides,1):lines += ['',f'## Slide {i} — {s["title"]}', '',f'**Quem:** {s["who"]}. **Tempo:** {s["seconds"]} segundos.', '', '**O que dizer**', '',s['say'],'','**Como dizer e o que mostrar**','',s['how'],'',f'**Código ou fonte:** {s["source"]}']
lines += ['', '## Demonstração no terminal', '', 'Execute a partir da raiz do repositório:', '', '```sh', 'make', './build/sequencial tests/matrizes/exemplo1.txt', './build/paralela tests/matrizes/exemplo1.txt 2', './build/paralela tests/matrizes/exemplo2.txt 2', '```', '', 'Saídas esperadas, na ordem: `3`, `3`, `4`. Se a demonstração atrasar, use as saídas capturadas no slide 12. Para mudar a quantidade de trabalhadores, troque o último argumento por `4`. A contagem deve continuar igual.', '', '## Respostas curtas para perguntas', '', '| Pergunta | Resposta |', '| --- | --- |', '| Por que oito vizinhos? | O enunciado considera conexão por lados e cantos. |', '| Por que não basta somar as faixas? | O mesmo objeto pode aparecer em duas faixas e ser contado duas vezes. |', '| Por que os rótulos não são 1, 2, 3? | Cada ID usa o índice global da célula inicial mais um; isso garante exclusividade. |', '| Usa processos ou threads? | Processos POSIX criados com fork. Não há Pthreads nesta solução. |', '| Precisa de mutex? | Não para os rótulos desta arquitetura: os filhos têm memória privada e o pai faz as uniões. |', '| Como funciona a conexão diagonal na fronteira? | Cada célula compara as colunas à esquerda, ao centro e à direita na faixa seguinte. |', '| Por que enviar só as bordas? | Conexões entre faixas só podem passar pela primeira ou última linha. |', '| O que garante que os filhos terminaram bem? | O pai verifica o retorno de waitpid e o status de saída. Se houver erro, não imprime contagem. |', '| Por que a busca não é recursiva? | Uma pilha no heap evita estourar a pilha de chamadas em objetos grandes. |', '| Por que a aceleração não é duas ou quatro vezes? | Só a busca local é paralela; leitura, coordenação, comunicação e consolidação têm custo. |', '| Foi validado em macOS? | Não. Esta validação e estas medições foram feitas em Linux. |', '| O que acontece com mais processos que linhas? | A quantidade de trabalhadores é limitada ao número de linhas. |', '', '## Ensaio', '', 'Façam um ensaio com cronômetro e as mesmas ações dos slides 6 e 10. Se passar de nove minutos, reduzam explicações de rank e detalhes de ponteiro, mantendo a conexão diagonal, a união sem duplicação e os resultados. Cada membro deve conseguir explicar a parte do colega.', '', '## Fontes e atualização', '', 'Enunciado original, páginas 1–9; código em `src/`; matrizes em `tests/matrizes/`; resultados em `results/`. A logo foi extraída do próprio PDF do enunciado, sem redesenho. As capturas do código incluem arquivo e linhas. Se o código ou os resultados mudarem, regenere o HTML com `python3 slides/scripts/build.py` e as capturas/PDF com o script de renderização.']
(OUT/'roteiro.md').write_text('\n'.join(lines)+'\n')
print(f'{len(slides)} slides; {sum(s["seconds"] for s in slides)} segundos; HTML e roteiro gerados.')
