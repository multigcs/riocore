#include <pthread.h>
#include <simulator.h>

int glsim_run(int argc, char** argv);

int main(int argc, char** argv) {
    pthread_t thread_id;
    pthread_create(&thread_id, NULL, simThread, NULL);

    glsim_run(argc, argv);
    sim_running = 0;
    pthread_join(thread_id, NULL);
    return 0;
}
