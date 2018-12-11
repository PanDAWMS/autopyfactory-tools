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


class RunningOnlyFilter(AnalyzerFilter):
    def filter(self, job):
        isrunning = False
        try:
            jobstatus = int(job['jobstatus'])
            if jobstatus == 2:
                isrunning = True
        except:
            pass
        return isrunning



def get_isfull():
    '''
    For each queue decide if it is full. 
        
    
    Return indexed boolean:
    
      {  'queuelabel1' : True, 
         'queuelabel2' : False 
      }
    
    '''
    jobdict = { }
    
    try:
      
        #pool = HTCondorPool(hostname='localhost', port='9618')
        sd = HTCondorSchedd()
        attlist = ['jobstatus','MATCH_APF_QUEUE','qdate','enteredcurrentstatus','clusterid','procid']
        cq = sd.condor_q(attribute_l = attlist)
        
        rrdict = get_recentrunning(cq)
        print("###################### recent runnning ##########################")
        pprint(rrdict)

        
        oidict = get_oldestidle(cq)
        print("###################### recent runnning ##########################")
        pprint(oidict)
          
    except:
        pass    
    return jobdict


def get_recentrunning(cq):
    '''
     Get the most recently started job for each queue by key. 
        
      {  'queuelabel1' : '1544551885',   # largest epoch time of all jobs in queue  
         'queuelabel2' : False 
      }

    '''
    si  = StatusInfo(cq)
    runningfilter = RunningOnlyFilter() 
    si = si.filter(runningfilter)
    si = si.indexby(IndexByKey('MATCH_APF_QUEUE'))    
    jobdict = si.getraw()
    return jobdict


def get_oldestidle(cq):
    '''
    Determine how old the oldest idle job is for each queue given by key.
    Determine when the last job to start started.  
     
    EnteredCurrentStatus = 1544551885  
    QDate  = 1544551885

      {  'queuelabel1' : '1544551885',   # smallest epoch time of all jobs in queue  
         'queuelabel2' : False 
      }    
    
    
    '''
    si  = StatusInfo(cq)
    idlefilter = IdleOnlyFilter() 
    si = si.filter(idlefilter)    
    si = si.indexby(IndexByKey('MATCH_APF_QUEUE'))    
    jobdict = si.getraw()
    return jobdict


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Calculates old idle for each queue indexed by key.')
    parser.add_argument("-H", "--headers", 
                    help="Prints the header of each column", 
                    action="store_true")
    parser.add_argument("-k", "--key", 
                    help="Key to index jobs by [MATCH_APF_QUEUE", 
                    action="store", 
                    dest='key', 
                    required=False, 
                    default='MATCH_APF_QUEUE')
    args = parser.parse_args()

    pprint(get_isfull())
