#!/usr/bin/env python

import commands
import getopt
import os
import re
import sys

# FIXME
#  * consider to specify a list of queues and/or list of dates
#    instead of everything
#


# DEFAULTS
BASEDIR = '/home/apf/factory/logs'
NEWDIR = '/tmp/apf-reverse-logstree'

try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["basedir=", "newdir="])
except getopt.GetoptError, err:
    print str(err)

for k,v in opts:
    if k == "--basedir":
    BASEDIR=v 
    if k == "--newdir":
    NEWDIR=v 

print BASEDIR
print NEWDIR

class QUEUE(object):
    def __init__(self, queue):
        self.queue = queue
        self.dates = []

LIST_QUEUES = {}

RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})?$")

for i in os.listdir(BASEDIR):
    if RE.match(i):
        DATE = i
        for queue in os.listdir('%s/%s' %(BASEDIR,DATE)):
            if queue not in LIST_QUEUES.keys():
                LIST_QUEUES[queue] = QUEUE(queue)
            LIST_QUEUES[queue].dates.append(DATE)


for q,Q in LIST_QUEUES.iteritems():
    cmd = 'mkdir -p %s/%s' %(NEWDIR, q) 
    commands.getoutput( cmd )
    for DATE in Q.dates:
        cmd = 'ln -s %s/%s/%s %s/%s/%s' %(BASEDIR, DATE , q ,NEWDIR, q, DATE) 
        commands.getoutput(cmd)
        #print (cmd)
