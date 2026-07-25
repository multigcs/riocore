/* Copyright 2024 Grug Huhler.  License SPDX BSD-2-Clause. */

ENTRY( _start )

MEMORY
{
   flash : ORIGIN = 0x00000000, LENGTH = 0x8000
   sram : ORIGIN = 0x20000000, LENGTH = 0x4000
}

 SECTIONS
 {
  .text   : { *(.text*)   } > flash
  .rodata : { *(.rodata*) } > flash
  __data_lma_start__ = ALIGN(4);
   .data   : AT (__data_lma_start__)
    {	
      __data_vma_start__ = .;
      *(.data*)
     __data_vma_end__ = .;
    } > sram

  .bss    :
    {
     __bss_vma_start__ = .;
    *(.bss*)
     __bss_vma_end__ = .;
    } > sram
 }
