
int error_handler(int retval) {
    if (retval < 0) {
        rtapi_print_msg(RTAPI_MSG_ERR, "%s: ERROR: pin export failed with err=%i\n", modname, retval);
        hal_exit(comp_id);
        return -1;
    }
}

int rtapi_app_main(void) {
    char name[HAL_NAME_LEN + 1];
    int retval = 0;
    int n = 0;
    data = hal_malloc(sizeof(data_t));
    comp_id = hal_init(modname);
    if (comp_id < 0) {
        rtapi_print_msg(RTAPI_MSG_ERR, "%s ERROR: hal_init() failed \n", modname);
        return -1;
    }
    register_signals();
    rtapi_snprintf(name, sizeof(name), "%s.update-freq", prefix);
    rtapi_snprintf(name, sizeof(name), "%s.readwrite", prefix);
    retval = hal_export_funct(name, rio_readwrite, data, 1, 0, comp_id);
    if (retval < 0) {
        rtapi_print_msg(RTAPI_MSG_ERR, "%s: ERROR: read function export failed\n", modname);
        hal_exit(comp_id);
        return -1;
    }
    rtapi_print_msg(RTAPI_MSG_INFO, "%s: installed driver\n", modname);
    hal_ready(comp_id);

    interface_init();

    rio_readwrite();

    return 0;
}

void rtapi_app_exit(void) {
    hal_exit(comp_id);
}

