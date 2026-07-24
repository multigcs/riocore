# serv
**minimal risc-v softcore**

minimal risc-v cpu for testing

* Keywords: risc-v softcore cpu
* NEEDS: fpga

## Pins:
*FPGA-pins*
### gpio0:

 * direction: output

### gpio1:

 * direction: output

### gpio2:

 * direction: output


## Options:
*user-options*
### name:
name of this plugin instance

 * type: str
 * default: 

### image:
hardware type

 * type: imgselect
 * default: generic

### ramsize:
memory size

 * type: int
 * min: 64
 * max: 2048
 * default: 64
 * unit: byte


## Signals:
*signals/pins in LinuxCNC*


## Interfaces:
*transport layer*


## Verilogs:
 * [serv.v](serv.v)
 * [ram32.v](ram32.v)
 * [ser_add.v](ser_add.v)
 * [ser_lt.v](ser_lt.v)
 * [ser_shift.v](ser_shift.v)
 * [serv_alu.v](serv_alu.v)
 * [serv_bufreg.v](serv_bufreg.v)
 * [serv_csr.v](serv_csr.v)
 * [serv_ctrl.v](serv_ctrl.v)
 * [serv_decode.v](serv_decode.v)
 * [serv_mem_if.v](serv_mem_if.v)
 * [serv_rf_if.v](serv_rf_if.v)
 * [serv_rf_ram_if.v](serv_rf_ram_if.v)
 * [serv_rf_ram.v](serv_rf_ram.v)
 * [serv_rf_top.v](serv_rf_top.v)
 * [serv_state.v](serv_state.v)
 * [serv_top.v](serv_top.v)
 * [shift_reg.v](shift_reg.v)
