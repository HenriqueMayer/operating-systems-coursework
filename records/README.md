# Gravação da apresentação de SISOP

Assista ao [vídeo completo da apresentação](apresentacao-final.mp4): **14 slides, aproximadamente 5 min 42 s**, em **1920 × 1080, 30 quadros/s, H.264 e AAC**. A montagem sincroniza as falas às animações da busca sequencial e da união dos componentes na fronteira. As [legendas em português](apresentacao-final.srt) são opcionais e também estão incorporadas ao MP4; podem ser ativadas ou desativadas no reprodutor.

Os [slides, roteiro e PDF](../slides/README.md) e as gravações de origem estão disponíveis neste repositório.

## Arquivos disponíveis

| Material | Conteúdo verificado |
| --- | --- |
| [apresentacao-final.mp4](apresentacao-final.mp4) | Vídeo completo dos slides 1 a 14, com as duas simulações, transições e capítulos por slide. |
| [apresentacao-final.srt](apresentacao-final.srt) | Legendas opcionais do vídeo completo, sincronizadas às falas e revisadas pelo roteiro. |
| [edicao.json](edicao.json) | Linha do tempo da apresentação completa: fontes de áudio, 28 cenas, animações, legendas e 14 capítulos. |
| [1-7.mp4](1-7.mp4) | Gravação original das falas dos slides 1 a 7. Contém apenas áudio AAC mono; não possui vídeo. |
| [8.flac](8.flac) a [14.flac](14.flac) | Gravações válidas dos slides 8 a 14, importadas do GNOME Sound Recorder; todas contêm sinal de áudio. |
| [14-edicao.flac](14-edicao.flac) | Fonte usada no encerramento do vídeo, com corte pontual da menção numérica divergente; `14.flac` preserva a gravação completa. |
| [scripts/render_slides.cjs](scripts/render_slides.cjs) | Captura os 14 slides e os estados das duas simulações diretamente do HTML original. |
| [scripts/montar_video.py](scripts/montar_video.py) | Montagem local com FFmpeg, normalização de volume, transições, capítulos e verificação de decodificação. Rejeita fontes inteiramente silenciosas. |

As falas dos slides 8 a 14 foram gravadas no GNOME Sound Recorder e copiadas para os respectivos arquivos FLAC desta pasta.

As falas dos slides 1 a 13 mantêm suas durações integrais; o encerramento usa `14-edicao.flac`, com o corte descrito abaixo. O volume é normalizado separadamente por fonte. As mudanças de slide seguem as pausas reais; o slide 6 acompanha os rótulos 1, 14 e 21. No slide 10, a animação mostra a soma local 5, destaca o contato diagonal, une os rótulos 10 e 28 e mantém a contagem 4 nos contatos repetidos. Os controles do navegador e os tempos previstos do roteiro ficam ocultos no vídeo.

O encerramento recebeu um corte pontual da menção numérica divergente, usando apenas a voz gravada. O original `14.flac` está preservado, e o slide apresenta o resultado correto de **3.813 execuções**. Os tempos e o motivo do corte estão registrados em `edicao.json`. A edição final tem **341,5573 s**.

A prévia parcial dos slides 1 a 7 e os sete arquivos silenciosos anteriores foram preservados no acervo local e são ignorados pelo Git. Um clone atual contém a apresentação completa e suas fontes; versões anteriores continuam no histórico.

## Reproduzir a montagem

Na raiz do repositório, com Python 3, Node.js, Playwright, Chrome e FFmpeg disponíveis:

```sh
python3 records/scripts/montar_video.py
```

Por padrão, o script lê `records/edicao.json` e gera `records/apresentacao-final.mp4`.

O script usa `build/video/` para imagens e arquivos intermediários, ignorados pelo Git. O renderer procura Playwright nos pacotes do Node e no runtime local do Codex; `NODE_PATH` permite fornecer outro diretório. `CHROME` permite escolher o navegador.

Os slides e suas simulações são reutilizados sem alterar [apresentacao.html](../slides/apresentacao.html) ou [apresentacao.pdf](../slides/apresentacao.pdf). A transcrição foi feita localmente com faster-whisper e o modelo small; os áudios não foram enviados a um serviço de transcrição. Essa ferramenta auxilia a marcar o tempo e não é necessária para reproduzir a montagem já definida no JSON.

O enunciado limita a apresentação a dez minutos e exige participação dos dois integrantes. O vídeo completo fica abaixo desse limite; os [slides em PDF](../slides/apresentacao.pdf) continuam sendo o material de slides exigido para a entrega.

## Registro

| Data | Registro |
| --- | --- |
| 2026-10-05 | `apresentacao-1-7.mp4`, `apresentacao-1-7.srt` e `edicao-1-7.json`: criada prévia sincronizada dos slides 1 a 7. Incluídos scripts de montagem e captura das simulações; identificados arquivos silenciosos de 8 a 14. |
| 2026-10-05 | `8.flac` a `14.flac`: importadas as gravações válidas do GNOME Sound Recorder. Preservados os arquivos silenciosos anteriores em `originais-silenciosos/`. |
| 2026-10-05 | `apresentacao-final.mp4`, `apresentacao-final.srt` e `edicao.json`: concluída a montagem integral dos 14 slides, com volume normalizado por fonte, animações sequencial e de fronteira, capítulos e legendas opcionais. |
| 2026-10-05 | `14-edicao.flac`: removida a menção numérica divergente do encerramento, com transição curta de áudio; preservados `14.flac` e o resultado correto nos slides. Duração final ajustada para aproximadamente 5 min 42 s. |
| 2026-10-06 | A prévia `apresentacao-1-7.mp4`, suas legendas e linha do tempo, e `originais-silenciosos/` passaram a ser arquivos locais ignorados pelo Git. Conservados o vídeo completo, os áudios utilizados e os scripts de reprodução. |
