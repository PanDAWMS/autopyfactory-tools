#!/bin/env python
import argparse
import libfactory
import logging
import sys
import traceback
from pprint import pprint
from libfactory.htcondorlib import HTCondorSchedd, HTCondorPool
from libfactory.info import StatusInfo, IndexByKey, AnalyzerFilter, AnalyzerMap, Count

'''
  JOB STATUS
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


class TargetInfo(object):
    def __init__(self):
        self.isfull = None         # boolean full or not 
        self.howfull = None        #floating value 0 - 1.0 ; 1.0 totally full ; 0 = empty
        self.newestrunning = None    # classad object of most recent running job
        self.oldestidle = None     #Classad object of oldest idle job
    

    def __repr__(self):
        nr = None
        oi = None
        try:
            nr = int(self.newestrunning['age'])
        except:
            pass
            
        try:    
            oi = int(self.oldestidle['age'])
        except:
            pass
        
        s = "TargetInfo: isfull=%s ,howfull=%s , newestrunning[age]=%s , oldestidle[age]=%s " % (self.isfull,
                                                                           self.howfull,
                                                                           nr,
                                                                           oi,
                                                                           )
        return s

class TargetStatus(object):
    '''
      Class to store and process the congestion status of HTCondor queues/targets.  
      Configuration parameters for heuristics provided on init, same for all targets. 
      
    '''
    def __init__(self):
        self.log = logging.getLogger()


    def get_howfull(self):
        '''
        Returns a value between 0 and 1 for how full the target is for all targets.  
        
        {  'queuelabel1' : 1.0 , 
           'queuelabel2' : .33 ,
           'queuelabel2' : .02 , 
        }
        '''


    def get_isfull(self):
        '''
        For each queue decide if it is full. 
        
        0th:    there is an idle job, and it has been idle for more 
                than X seconds, where X is related to the size of the target resource. 
        1st:    there is an idle job, and it has been idle for more than Y seconds, and
                the last job to start was more than Z seconds ago
        
        
        X = 360
        Y = 2000
        
        if Q does not have idle:
            FULL = False
        if Q has started a job within X seconds:
            FULL = False
        if Q has NOT started a job within X seconds AND Q has idle job older than Y seconds:
            FULL = True
              
        
        Return indexed boolean:
        
          {  'queuelabel1' : True, 
             'queuelabel2' : False 
          }
        
        '''
        queuedict = {}
        
        try:
            #pool = HTCondorPool(hostname='localhost', port='9618')
            sd = HTCondorSchedd()
            attlist = ['jobstatus','MATCH_APF_QUEUE','qdate','enteredcurrentstatus','clusterid','procid','serverTime']
            cq = sd.condor_q(attribute_l = attlist)
            
            rrdict = self.get_recentrunning(cq)      
            self.log.debug('####################### rrdict ####################' )
            self.log.debug(rrdict)
            
            oidict = self.get_oldestidle(cq)
            self.log.debug('####################### oidcit ####################' )
            self.log.debug(oidict)
            queuedict = self._build_queuedict(rrdict, oidict)
            self.log.debug('###################### queuedict one ####################')
            self.log.debug(queuedict)
            queuedict = self._calc_isfull(queuedict)
            self.log.debug('##################### queuedict after isfull calc ####################')
            self.log.debug(queuedict)
            queuedict = self._calc_howfull(queuedict)
            self.log.debug('#################### queuedict after howfull calc ####################')
            self.log.debug(queuedict)
            
        except:
            self.log.debug(traceback.format_exc(None))   
        return queuedict

    def _build_queuedict(self, runningdict, idledict):
        '''
        queuedict = 
        
          {      
             'queuelabel1' : [ isFull, howFull, newestrunningjob, oldestidlejob ] 
             'queuelabel2' : [ isFull, howFull, newestrunningjob, oldestidlejob ] 
          }
          
          }
        
        
        '''
        # build empty structure containing all queues. 
        queuedict = {}
        for q in runningdict.keys():
            queuedict[q] = TargetInfo()
        for q in idledict.keys():
            queuedict[q] = TargetInfo()
        # fill in values
        
        for q in runningdict.keys():
            queuedict[q].newestrunning = runningdict[q]
            
        for q in idledict.keys():
            queuedict[q].oldestidle = idledict[q]
        return queuedict


    def _calc_isfull(self, queuedict):
        for q in queuedict.keys():
            ti = queuedict[q]
            ti.isfull = False
            
            if ti.oldestidle is None:
                ti.isfull = False
            
            else:
                try:
                    agestr = ti.oldestidle['age'] 
                    if int( agestr  ) > 360 :
                        ti.isfull = True 
                    
                    agestr = ti.newestrunning['age'] 
                    if int(agestr) < 120 :
                        ti.isfull = False
                except:
                    pass
        return queuedict

    def _calc_howfull(self, queuedict):
        
        return queuedict



    def get_recentrunning(self, cq):
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
            #print("Type of job is %s" % type(newest))
            del newest['MyType']
            del newest['TargetType']
            newest['age'] = int(newest['ServerTime']) - int(newest['enteredcurrentstatus'])
            jobdict[q] = newest
        return jobdict


    def get_oldestidle(self, cq):
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
            # newest is now  [ jobstatus = 1; MATCH_APF_QUEUE = "ANALY_BNL_SHORT-gridgk07.racf.bnl.gov"; ServerTime = 1544627506; enteredcurrentstatus = 1544627388; clusterid = 398446; procid = 0; qdate = 1544627388; MyType = "Job"; TargetType = "Machine" ]
            #print("Type of job is %s" % type(oldest))
            del oldest['MyType']
            del oldest['TargetType']
            oldest['age'] = int(oldest['ServerTime']) - int(oldest['enteredcurrentstatus'])
            jobdict[q] = oldest
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
    
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    ts = TargetStatus()
    pprint(ts.get_isfull())

