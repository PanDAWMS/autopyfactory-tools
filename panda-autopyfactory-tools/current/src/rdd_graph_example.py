#!/usr/bin/python

#
#  explanation of variables in "rrdtool graph" command
#  can be found here
#
#       https://calomel.org/rrdtool.html
#



#
#   rrdtool create apf_db.rrd \
#   --step 360 \
#   DS:activated:GAUGE:720:0:100000 \
#   DS:running:GAUGE:720:0:100000 \
#   DS:pending:GAUGE:720:0:100000 \
#   DS:submitted:GAUGE:720:0:100000 \
#   RRA:MAX:0.5:1:100
# 


import commands
import sys
import os


os.environ['TZ'] = 'UTC'

#out = commands.getoutput('rrdtool fetch apf_db.rrd MAX')
#values = out.split('\n')[1:]
#print values


cmd='/usr/bin/rrdtool graph apf_plot_activated.png '
cmd += ' -w 885 -h 151 -a PNG --slope-mode '
cmd += ' --font DEFAULT:7: --watermark "`date`"'
cmd += ' --title "APF Activity: ANALY_BNL_SHORT-gridgk01"'
cmd += ' --vertical-label "# Activated jobs" --lower-limit 0'
cmd += ' --start -36000 --end now'
cmd += ' --right-axis 1:0'
cmd += ' --right-axis-label "# Activated jobs"'
cmd += ' --x-grid MINUTE:6:HOUR:1:MINUTE:60:0:%R'
cmd += ' --alt-y-grid --rigid '
cmd += ' DEF:activated=apf_db.rrd:activated:MAX '
cmd += ' LINE1:activated#0000FF:"#Activated" '
print commands.getoutput(cmd)


cmd='/usr/bin/rrdtool graph apf_plot_pending_running.png '
cmd += ' -w 885 -h 151 -a PNG --slope-mode '
cmd += ' --font DEFAULT:7: --watermark "`date`"'
cmd += ' --title "APF Activity: ANALY_BNL_SHORT-gridgk01"'
cmd += ' --vertical-label "# Pending pilots" --lower-limit 0'
cmd += ' --right-axis 1:0'
cmd += ' --right-axis-label "# Running pilots"'
cmd += ' --start -36000 --end now'
cmd += ' --x-grid MINUTE:6:HOUR:1:MINUTE:60:0:%R'
cmd += ' --alt-y-grid --rigid '
cmd += ' DEF:pending=apf_db.rrd:pending:MAX '
cmd += ' DEF:running=apf_db.rrd:running:MAX '
cmd += ' LINE1:pending#0000FF:"#Pending" '
cmd += ' LINE2:running#00FF00:"#Running" '
print commands.getoutput(cmd)



cmd='/usr/bin/rrdtool graph apf_plot_submitted.png '
cmd += ' -w 885 -h 151 -a PNG --slope-mode '
cmd += ' --font DEFAULT:7: --watermark "`date`"'
cmd += ' --title "APF Activity: ANALY_BNL_SHORT-gridgk01"'
cmd += ' --vertical-label "# Pilot submitted" --lower-limit 0'
cmd += ' --right-axis 1:0'
cmd += ' --right-axis-label "# Pilot submitted"'
cmd += ' --start -36000 --end now'
cmd += ' --x-grid MINUTE:6:HOUR:1:MINUTE:60:0:%R'
cmd += ' --alt-y-grid --rigid '
cmd += ' DEF:submitted=apf_db.rrd:submitted:MAX '
cmd += ' LINE1:submitted#0000FF:"#Submitted" '
print commands.getoutput(cmd)


