#!/bin/env python
import libfactory
import logging
from pprint import pprint
from libfactory.htcondorlib import HTCondorSchedd, HTCondorPool
from libfactory.info import StatusInfo, IndexByKey, AnalyzerFilter, AnalyzerMap, Count
import argparse

'''
 idle = 1
 running = 2

'''


class IdleOnlyFilter(AnalyzerFilter):
    def filter(self, job):
        isidle = False
        try:
            jobstatus = int(job['jobstatus'])
            if jobstatus == 1:
                isidle = True
        except:
            pass
        return isidle



def get_is_full():
    '''
    For each queue decide if it is full. 
    Return indexed boolean:
    
      {  'queuelabel1' : True, 'queuelabel2' : False }
    
    '''


def get_lastrun():
    '''
    Determine how old the oldest idle job is for each queue given by key.
    Determine when the last job to start started.  
     
    EnteredCurrentStatus = 1544551885
    QDate  = 1544551885
    
    '''

    try:
      
        #pool = HTCondorPool(hostname='localhost', port='9618')
        sd = HTCondorSchedd()
        attlist = ['jobstatus','MATCH_APF_QUEUE','qdate','enteredcurrentstatus']
        cq = sd.condor_q(attribute_l = attlist)
        si = StatusInfo(cq)
        idlefilter = IdleOnlyFilter()  
        si = si.filter(idlefilter)
        si = si.indexby(IndexByKey('MATCH_APF_QUEUE'))    
        #si = si.process(Count())
        jobdict = si.getraw()
    except:
        pass    
    return jobdict




if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Calculates old idle for each queue indexed by key.')
    parser.add_argument("-H", "--headers", 
                    help="Prints the header of each column", 
                    action="store_true")
    parser.add_argument("-k", "--key", 
                    help="Key to index jobs by [MATCH_APF_QUEUE", 
                    action="store", 
                    dst='key', 
                    required=False, 
                    default='MATCH_APF_QUEUE')
    args = parser.parse_args()

    print(get_lastrun())
