#!/bin/bash 


rrdtool create apf_db.rrd \
--step 360 \
DS:activated:GAUGE:720:0:100000 \
DS:running:GAUGE:720:0:100000 \
DS:pending:GAUGE:720:0:100000 \
DS:submitted:GAUGE:720:0:100000 \
RRA:MAX:0.5:1:100
