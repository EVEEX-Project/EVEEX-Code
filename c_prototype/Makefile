all: run clean

build:
	gcc main.c -o main.o -lm

dev-build:
	gcc main.c -o main.o -lm -Wall

run: build
	./main.o

clean:
	rm main.o