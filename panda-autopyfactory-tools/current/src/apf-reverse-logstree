#!/usr/bin/env python

import os
import re
import commands

# FIXME
#
#  * BASEDIR and NEWBASEDIR should be read from configfile
#
#  * consider to specify a list of queues and/or list of dates
#    instead of everything
#


BASEDIR = '/home/apf/factory/logs'
NEWBASEDIR = '/tmp/l1'

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
        commands.getoutput('mkdir %s/%s' %(NEWBASEDIR, q) )
        for DATE in Q.dates:
                commands.getoutput('ln -s %s/%s/%s %s/%s/%s' %(BASEDIR, DATE , q ,NEWBASEDIR, q, DATE) )
                #print ('ln -s %s/%s/%s %s/%s/%s' %(BASEDIR, DATE , q ,NEWBASEDIR, q, DATE) )
