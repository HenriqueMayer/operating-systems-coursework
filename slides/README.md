# Apresentação da dupla

Abra [apresentacao.html](apresentacao.html) no navegador. O arquivo contém os estilos, scripts, logo e capturas do código, sem depender de internet ou dos arquivos de assets para ser apresentado.

- [roteiro.md](roteiro.md): falas e ações de cada membro, por slide; previsão de 8 min 50 s.
- [apresentacao.pdf](apresentacao.pdf): versão estática para a entrega exigida pelo enunciado.

Use as setas para mudar de slide, R para abrir o roteiro, F para tela cheia e os botões das duas simulações para avançar seus passos. Na impressão, as simulações mostram o resultado final.

A logo foi extraída da página 1 do PDF original do enunciado, com sua máscara de transparência. Os prints mostram trechos reais de src/, com nome do arquivo e linhas. As saídas em assets/saidas.txt foram capturadas dos executáveis; os números de desempenho vêm de results/benchmark.json. As simulações reproduzem a marcação do código em JavaScript, sem executar C no navegador.

## Atualizar os arquivos

Depois de alterar código, resultados ou conteúdo, compile com `make`. Para atualizar também as capturas e o PDF, use Python 3, Node.js, Playwright e Chrome:

```sh
python3 slides/scripts/build.py --text-code
node slides/scripts/render.cjs
python3 slides/scripts/build.py
node slides/scripts/render.cjs --final
```

O script de renderização usa `/usr/bin/google-chrome` por padrão; a variável `CHROME` permite escolher outro executável. A primeira renderização captura os trechos; a segunda verifica navegação, roteiro, simulações, visualização em celular, ausência de recursos remotos e exporta o PDF. As capturas de conferência ficam em /tmp/sisop-slides-qa.

Edite as falas em scripts/build.py, os estilos em scripts/style.css e o comportamento em scripts/presentation.js. O gerador produz novamente o HTML, o roteiro e assets/conteudo.json.
