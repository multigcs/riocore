 ENTRY( _start )
 SECTIONS
 {
 /* text: test code section */
 . = 0x0;
 .text :
 {
 *(.text)
 }
 .sbss :
 {
 *(.sbss)
 }
 .bss :
 {
 *(.bss)
 }
 .rodata :
 {
 *(.rodata)
 }
 .srodata :
 {
 *(.srodata)
 }
 /* data: Initialized data segment */
 .data :
 {
 *(.data)
 }
 /* End of uninitalized data segement */
 _end = .;
 }
