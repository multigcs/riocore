
#include <rtapi.h>
#include <rtapi_app.h>
#include <hal.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <termios.h>
#include <dlfcn.h>
#include <linux/limits.h>

/*
rio - dynamic component loader

compile and load the rio component from the Configuration Folder on startup

*/

void *so_handle;
int (*_rtapi_app_main)(void);
void (*_rtapi_app_exit)(void);
char cwd[PATH_MAX];
char so_file[PATH_MAX];

#define MAX_COMPNAMES 10
static char *comp_names[MAX_COMPNAMES];
RTAPI_MP_ARRAY_STRING(comp_names, MAX_COMPNAMES, "component names.")

static int comp_id;

int rtapi_app_main(void) {
    comp_id = hal_init("rio");

    char *error;
    int ret = 0;
    int i = 0;
    for(i = 0, ret = 0; ret == 0 && i<MAX_COMPNAMES && comp_names[i] && *comp_names[i]; i++) {
        printf("# compiling and loading rio component (%s)..", comp_names[i]);
        // get working directory
        if (getcwd(cwd, sizeof(cwd)) == NULL) {
            printf(".failed\n");
            fputs("getcwd() error\n", stderr);
            return -1;
        }
        // compile the rio component
        char compile_str[1024];
        sprintf(compile_str, "halcompile --compile %s.c > /dev/null", comp_names[i]);
        if (system(compile_str) != 0) {
            printf(".failed\n");
            return -1;
        }
        // set absolut path to the rio component
        if (snprintf(so_file, sizeof(so_file), "%s/%s.so", cwd, comp_names[i]) < 0) {
            printf(".failed\n");
            fputs("getcwd() error\n", stderr);
            return -1;
        }
        // open .so file
        so_handle = dlopen(so_file, RTLD_LAZY);
        if (!so_handle) {
            printf(".failed\n");
            fputs (dlerror(), stderr);
            return -1;
        }

        // get symbols
        _rtapi_app_main = dlsym(so_handle, "rtapi_app_main");
        if ((error = dlerror()) != NULL)  {
            printf(".failed\n");
            fputs(error, stderr);
            return -1;
        }
        _rtapi_app_exit = dlsym(so_handle, "rtapi_app_exit");
        if ((error = dlerror()) != NULL)  {
            printf(".failed\n");
            fputs(error, stderr);
            return -1;
        }
        (*_rtapi_app_main)();
        printf(".done\n");
    }

    hal_ready(comp_id);
    return 0;
}

void rtapi_app_exit(void) {
	// exit component

    char *error;
    int ret = 0;
    int i = 0;
    for(i = 0, ret = 0; ret == 0 && i<MAX_COMPNAMES && comp_names[i] && *comp_names[i]; i++) {
        printf("# unloading rio component (%s)..", comp_names[i]);
        // set absolut path to the rio component
        if (snprintf(so_file, sizeof(so_file), "%s/%s.so", cwd, comp_names[i]) < 0) {
            printf(".failed\n");
            fputs("getcwd() error\n", stderr);
            return;
        }
        // open .so file
        so_handle = dlopen(so_file, RTLD_LAZY);
        if (!so_handle) {
            printf(".failed\n");
            fputs (dlerror(), stderr);
            return;
        }
        _rtapi_app_exit = dlsym(so_handle, "rtapi_app_exit");
        if ((error = dlerror()) != NULL)  {
            printf(".failed\n");
            fputs(error, stderr);
            return;
        }
        (*_rtapi_app_exit)();
        printf(".done\n");
    }

    hal_exit(comp_id);

}
