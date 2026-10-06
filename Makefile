CC = cc
CFLAGS = -O2 -std=c89 -Wall -Wextra -pedantic
LDFLAGS =
PYTHON = python3

.PHONY: all test sanitize benchmark clean
all: build/sequencial build/paralela

build:
	mkdir -p build

build/sequencial: src/sequencial.c src/matrix.c src/matrix.h | build
	$(CC) $(CFLAGS) src/sequencial.c src/matrix.c $(LDFLAGS) -o $@

build/paralela: src/paralela.c src/matrix.c src/matrix.h | build
	$(CC) $(CFLAGS) src/paralela.c src/matrix.c $(LDFLAGS) -o $@

test: all
	$(PYTHON) tests/validate.py

sanitize:
	$(MAKE) clean
	$(MAKE) CFLAGS="-O1 -g -std=c89 -Wall -Wextra -pedantic -fsanitize=address,undefined -fno-sanitize-recover=all" LDFLAGS="-fsanitize=address,undefined" test

benchmark: all
	$(PYTHON) tests/benchmark.py

clean:
	rm -f build/sequencial build/paralela build/fault-memory build/fault-fork
