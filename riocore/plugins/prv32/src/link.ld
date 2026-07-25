ENTRY( _start )
SECTIONS
{
 . = 0x0;
 .text : { *(.text) }
 .sbss : { *(.sbss) }
 .bss : { *(.bss) }
 .rodata : { *(.rodata) }
 .srodata :{ *(.srodata) }
 .data : { *(.data) }
 _end = .;
}
