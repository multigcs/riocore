
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

int rtapi_app_main(void) {
    char *error;
	printf("# compiling and loading rio component..");
	// get working directory
    if (getcwd(cwd, sizeof(cwd)) == NULL) {
		printf(".failed\n");
        fputs("getcwd() error\n", stderr);
        return -1;
    }
	// compile the rio component
	if (system("halcompile --compile riocomp.c > /dev/null") != 0) {
		printf(".failed\n");
        return -1;
	}
	// set absolut path to the rio component
    if (snprintf(so_file, sizeof(so_file), "%s/riocomp.so", cwd) < 0) {
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
	printf(".done\n");

	// init component
    return (*_rtapi_app_main)();
}

void rtapi_app_exit(void) {
	// exit component
    (*_rtapi_app_exit)();
}
