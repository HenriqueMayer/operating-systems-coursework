# Medicao de desempenho

Matriz 800 × 800, densidade 0,45, semente 20260929. Cinco execuções após aquecimento; mediana do tempo total, incluindo leitura, criação de processos, comunicação e consolidação.

| Versão | Processos trabalhadores | Mediana (s) | Aceleração |
| --- | ---: | ---: | ---: |
| sequencial | 1 | 0.062263 | 1.000 |
| paralela | 2 | 0.056911 | 1.094 |
| paralela | 4 | 0.056507 | 1.102 |

Resultados locais sujeitos a carga e hardware. A paralela pode ser mais lenta devido à criação dos processos, transferência das bordas e consolidação sequencial. Esta medição não comprova escalabilidade em outros tamanhos.

Dados e ambiente: [benchmark.json](benchmark.json). Reproduzir com `make benchmark` em uma compilação otimizada, sem sanitizadores.
