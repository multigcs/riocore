
all: simulator

clean:
	rm -f simulator

simulator: main.c simulator.c glsim.c riocore.c interface.c
	gcc -o simulator -Os -I. main.c simulator.c glsim.c riocore.c interface.c  -lm -lGL -lGLU -lglut

simulator_run: simulator
	./simulator
