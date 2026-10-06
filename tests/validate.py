"""Comparacao com referencia independente e regressao de entradas/erros."""
import itertools
import os
from pathlib import Path
import random
import shlex
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def count_objects(matrix):
    # Busca em largura independente do flood fill e do Union-Find em C.
    remaining = {(r, c) for r, row in enumerate(matrix)
                 for c, value in enumerate(row) if value == 1}
    objects = 0
    while remaining:
        objects += 1
        queue = [remaining.pop()]
        for row, col in queue:
            for dr, dc in itertools.product((-1, 0, 1), repeat=2):
                cell = (row + dr, col + dc)
                if cell in remaining:
                    remaining.remove(cell)
                    queue.append(cell)
    return objects


def serialize(matrix):
    return (f"{len(matrix)} {len(matrix[0])}\n" +
            "\n".join(" ".join(map(str, row)) for row in matrix) + "\n")


def execute(binary, path, processes=None):
    args = [str(ROOT / "build" / binary), str(path)]
    if processes is not None:
        args.append(str(processes))
    return subprocess.run(args, capture_output=True, text=True, timeout=20)


def validate_faults(path):
    # --wrap e exclusivo do linker GNU: usado apenas nos testes Linux.
    if not sys.platform.startswith("linux"):
        print("Injecao de falhas: nao executada (requer linker GNU/Linux).")
        return
    cc = shlex.split(os.environ.get("CC", "cc"))
    for kind in ("memory", "fork"):
        binary = ROOT / "build" / f"fault-{kind}"
        subprocess.run(cc + ["-std=c89", "-Wall", "-Wextra", "-pedantic",
                              "src/paralela.c", "src/matrix.c",
                              "tests/faults.c", f"-DFAIL_{kind.upper()}",
                              f"-Wl,--wrap={'malloc' if kind == 'memory' else 'fork'}",
                              "-o", str(binary)], cwd=ROOT, check=True)
        result = execute(f"fault-{kind}", path, 2)
        assert result.returncode != 0 and not result.stdout, (kind, result)
        print(f"Falha simulada de {kind}: encerramento com erro, sem contagem.")


def main():
    cases = []
    for index in range(1, 6):
        tokens = list(map(int, (ROOT / f"tests/matrizes/exemplo{index}.txt").read_text().split()))
        rows, cols = tokens[:2]
        values = tokens[2:]
        assert len(values) == rows * cols
        matrix = [values[r * cols:(r + 1) * cols] for r in range(rows)]
        assert count_objects(matrix) == index + 2
        cases.append(matrix)
    for bits in itertools.product((0, 1), repeat=9):
        cases.append([list(bits[i:i + 3]) for i in (0, 3, 6)])
    rng = random.Random(20260929)
    for _ in range(200):
        rows, cols = rng.randint(1, 35), rng.randint(1, 35)
        density = rng.random()
        cases.append([[int(rng.random() < density) for _ in range(cols)]
                      for _ in range(rows)])
    cases.extend([
        [[1] * 200000], [[1] * 200 for _ in range(200)],
        [[0] * 15 for _ in range(10)],
        [[int(r == c) for c in range(50)] for r in range(50)],
        [[int(r % 2 == 0 and c % 2 == 0) for c in range(21)] for r in range(17)],
        [[1], [0], [1], [1], [0]],
    ])
    runs = 0
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "matrix.txt"
        for matrix in cases:
            path.write_text(serialize(matrix))
            expected = str(count_objects(matrix)) + "\n"
            configurations = [("sequencial", None)] + [
                ("paralela", n) for n in sorted({1, 2, 3, len(matrix), len(matrix) + 3})]
            for binary, processes in configurations:
                result = execute(binary, path, processes)
                assert result.returncode == 0 and result.stdout == expected and not result.stderr, (
                    binary, processes, result.returncode, expected, result.stdout, result.stderr)
                runs += 1
        for content in ("", "0 3\n", "-1 2\n", "2 x\n", "2 2\n1 1 1\n",
                        "1 3\n1 2 1\n", "1 1\n-1\n", "1 1\n1 0\n",
                        "1 1\n1 lixo\n", "18446744073709551616 2\n",
                        "18446744073709551615 2\n", "65536 65536\n"):
            path.write_text(content)
            for binary, n in (("sequencial", None), ("paralela", 2)):
                result = execute(binary, path, n)
                assert result.returncode != 0 and not result.stdout, (content, binary, result)
        path.write_text("2 2\n1 0\n0 1\n")
        for n in ("0", "-1", "abc", "2abc", "18446744073709551616"):
            result = execute("paralela", path, n)
            assert result.returncode != 0 and not result.stdout
        for binary in ("sequencial", "paralela"):
            assert execute(binary, Path(directory) / "ausente.txt").returncode != 0
            result = subprocess.run([str(ROOT / "build" / binary)], cwd=ROOT,
                                    capture_output=True, text=True, timeout=20)
            assert result.returncode == 0 and result.stdout == "3\n"
        validate_faults(path)
    print(f"PASS: {len(cases)} matrizes, {runs} execucoes C; entradas invalidas e falhas verificadas.")


if __name__ == "__main__":
    main()
