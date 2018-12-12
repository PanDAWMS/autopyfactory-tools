#!/bin/env python
import argparse
import libfactory
import logging
import traceback
from pprint import pprint
from libfactory.htcondorlib import HTCondorSchedd, HTCondorPool
from libfactory.info import StatusInfo, IndexByKey, AnalyzerFilter, AnalyzerMap, Count


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
            print(traceback.format_exc(None))   
        return isidle


class RunningOnlyFilter(AnalyzerFilter):
    def filter(self, job):
        isrunning = False
        try:
            jobstatus = int(job['jobstatus'])
            if jobstatus == 2:
                isrunning = True
        except:
            print(traceback.format_exc(None))   
            
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
        attlist = ['jobstatus','MATCH_APF_QUEUE','qdate','enteredcurrentstatus','clusterid','procid','serverTime']
        cq = sd.condor_q(attribute_l = attlist)
        
        rrdict = get_recentrunning(cq)
        print("###################### recent runnning ##########################")
        pprint(rrdict)

        
        oidict = get_oldestidle(cq)
        print("###################### oldest idle ##########################")
        pprint(oidict)
          
    except:
        print(traceback.format_exc(None))   
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
    
    for q in jobdict.keys():
        newest = None
        joblist = jobdict[q]
        for j in joblist:
            if not newest:
                newest = j
            else:
                if int( j['enteredcurrentstatus'] ) > int( newest['enteredcurrentstatus'] ):
                    newest = j
        # newest is now  [ jobstatus = 1; MATCH_APF_QUEUE = "ANALY_BNL_SHORT-gridgk07.racf.bnl.gov"; ServerTime = 1544627506; enteredcurrentstatus = 1544627388; clusterid = 398446; procid = 0; qdate = 1544627388; MyType = "Job"; TargetType = "Machine" ]
        print("Type of job is %s" % type(newest))
        jobdict[q] = [newest]
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
    
    for q in jobdict.keys():
        oldest = None
        joblist = jobdict[q]
        for j in joblist:
            if not oldest:
                oldest = j
            else:
                if int( j['enteredcurrentstatus'] ) > int( oldest['enteredcurrentstatus'] ):
                    oldest = j
        jobdict[q] = [oldest]
    return jobdict



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Calculates oldest idle, recently run for each queue indexed by key.')
    parser.add_argument("-H", "--headers", 
                    help="Prints the header of each column", 
                    action="store_true")
    parser.add_argument("-k", "--key", 
                    help="Key to index jobs by [MATCH_APF_QUEUE]", 
                    action="store", 
                    dest='key', 
                    required=False, 
                    default='MATCH_APF_QUEUE')
    args = parser.parse_args()

    pprint(get_isfull())

