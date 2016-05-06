#!/bin/bash

# prints the section portion in the config files
# for a given pattern to be matched in the [ HEAD ]
# of the section.
# For example, 
#  apf-print-qconf.sh ANALY_BNL queues.conf
# prints all queues sections for all 
# ANALY_BNL_LONG, ANALY_BNL_SHORT, ANALY_BNL_MCORE,etc. queues 


QUEUE=$1
shift
FILENAME=$@

sed -n "/^\[.*$QUEUE.*]$/,/^$/p" $FILENAME

