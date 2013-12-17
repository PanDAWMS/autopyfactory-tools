#!/bin/bash 

rrdtool update apf_db.rrd --template activated:running:pending:submitted N:$1:$2:$3:$4
#date >> log
#echo "$1 $2 $3 $4" >> log


