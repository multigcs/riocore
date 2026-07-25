/* Copyright 2024 Grug Huhler.  License SPDX BSD-2-Clause. */

extern unsigned int __data_lma_start__;
extern unsigned int __data_vma_start__;
extern unsigned int __data_vma_end__;
extern unsigned int __bss_vma_start__;
extern unsigned int __bss_vma_end__;
extern int main(void);

void cont_startup(void)
{
  char *lma_src, *vma_dst, *vma_last;

  /* Copy initialized mutable data from flash to sram */

  lma_src = (char *) &__data_lma_start__;
  vma_dst = (char *) &__data_vma_start__;
  vma_last = (char *) &__data_vma_end__;

  while (vma_dst < vma_last) {
    *vma_dst++ = *lma_src++;
  }

  /* clear bss (uninitialized data) */
  vma_dst = (char *) &__bss_vma_start__;
  vma_last = (char *) &__bss_vma_end__;

  while (vma_dst < vma_last) {
    *vma_dst++ = 0;
  }

  main();
}


