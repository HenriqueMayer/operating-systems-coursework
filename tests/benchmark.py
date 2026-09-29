"""Mede os executaveis sobre a mesma matriz; inclui leitura e criacao de processos."""
import json
import platform
import random
import statistics
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    rng = random.Random(20260929)
    size = 800
    with tempfile.TemporaryDirectory() as directory:
        matrix = Path(directory) / "large.txt"
        matrix.write_text(f"{size} {size}\n" + "\n".join(
            " ".join(str(int(rng.random() < 0.45)) for _ in range(size))
            for _ in range(size)) + "\n")
        records = []
        expected = None
        for binary, processes in (("sequencial", None), ("paralela", 2), ("paralela", 4)):
            args = [str(ROOT / "build" / binary), str(matrix)]
            if processes is not None:
                args.append(str(processes))
            subprocess.run(args, check=True, capture_output=True, text=True)
            samples = []
            for _ in range(5):
                start = time.perf_counter()
                result = subprocess.run(args, check=True, capture_output=True, text=True)
                samples.append(time.perf_counter() - start)
                if expected is None:
                    expected = result.stdout
                assert result.stdout == expected
            records.append({"version": binary, "processes": processes,
                            "samples_seconds": samples, "median_seconds": statistics.median(samples)})
    sequential = records[0]["median_seconds"]
    for record in records:
        record["speedup"] = sequential / record["median_seconds"]
    results = ROOT / "results"
    results.mkdir(exist_ok=True)
    (results / "benchmark.json").write_text(json.dumps({
        "system": platform.platform(), "compiler": subprocess.check_output(["cc", "--version"], text=True).splitlines()[0],
        "matrix": {"rows": size, "cols": size, "density": 0.45, "seed": 20260929},
        "objects": int(expected), "repetitions": 5,
        "scope": "Tempo total do executavel, incluindo entrada, processos, IPC e consolidacao.",
        "records": records}, indent=2) + "\n")
    lines = ["# Medicao de desempenho", "", "Matriz 800 × 800, densidade 0,45, semente 20260929. Cinco execuções após aquecimento; mediana do tempo total, incluindo leitura, criação de processos, comunicação e consolidação.", "", "| Versão | Processos trabalhadores | Mediana (s) | Aceleração |", "| --- | ---: | ---: | ---: |"]
    for r in records:
        lines.append(f"| {r['version']} | {r['processes'] or 1} | {r['median_seconds']:.6f} | {r['speedup']:.3f} |")
    lines += ["", "Resultados locais sujeitos a carga e hardware. A paralela pode ser mais lenta devido à criação dos processos, transferência das bordas e consolidação sequencial. Esta medição não comprova escalabilidade em outros tamanhos.", "", "Dados e ambiente: [benchmark.json](benchmark.json). Reproduzir com `make benchmark` em uma compilação otimizada, sem sanitizadores."]
    (results / "desempenho.md").write_text("\n".join(lines) + "\n")
    print("Resultados gravados em results/desempenho.md e results/benchmark.json")


if __name__ == "__main__":
    main()
