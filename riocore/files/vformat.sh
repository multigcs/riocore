#!/bin/bash
#
#

for FILE in $@
do
    echo $FILE
    verible-verilog-format --assignment_statement_alignment flush-left --module_net_variable_alignment flush-left --indentation_spaces 4 $FILE > $FILE.formated && mv $FILE.formated $FILE || rm $FILE.formated
done

