#!/bin/env python

import copy
import subprocess
import time

import htcondor


# =============================================================================
#                        CONDOR CLASSES
# =============================================================================

class CondorQuery(object):
    """
    This class is a common interface for all classes implementing 
    HTCondor queries (condor_q, condor_status, ...)
    It contains the common functionalities.
    For the specific implementation of the query, 
    there should be child classes.
    That query code is to be implemented in method

       _query( )

    Neither this class or any of the children ones 
    are meant to interpret the output of the query.
    For that, the class hosts a list of objects,
    one per line in the output of the query.
    Each type of these objects represents the meaning
    of the particular query: a job, a slot, etc.
    Those objects are the ones that must know how to 
    process the output of the query.
    """

    def __init__(self):

        self.container = Container()


    def run(self):

        self._query()
        self._store()
        self._sort()


    def _query(self):
        raise NotImplementedError


    def _store(self):
        """
        The code for this method is always almost the same. 
        It will look like this

            def _store(self):
                for job_classad in self.out:
                    dict_attr = self._clean(job_classad)
                    new_item = XYZ(dict_attr)
                    self.container.add(new_item)

        where XYZ is the actual kind of objects being stored:
        Job()'s, Slot()'s, ...
     
        We force this method to be implemented by the child classes
        because if will add objects to the self.container list,
        but these objects are of different classes each time:
           Job, Slot, ...
        So, to have it implemented here, we would need a way to pass
        it somehow. For example, passing the class to the __init__
        via the super( ) call. Something like this

           class Child:
               def __init__(self):
                   super(Child, self).__init__(Job)
     
        and this class will receive it, like this

           class CondorQuery:
               def __init__(self, ItemType):
                   self.ItemType = ItemType

               def _store(self):
                   for job_classad in self.out:
                       dict_attr = self._clean(job_classad)
                       new_item = ItemType(dict_attr)
                       self.container.add(new_item)

        Another way would be passing a string, and from there
        getting the right object like a plugin. 

        In any case, forcing it to be re-implemented on every child
        class seems to be a little bit cleaner
        """
        raise NotImplementedError


    def _clean(self, job_classad):
        """
        this method is to clean the dictionary in the classad

        The output returned by htcondor python query( ) methods 
        may contain more key:value pairs that we want

        Also, some of them could be missing, so we add a 
             "undefined"
        string in it.

        Also, we force all values to be strings. 
        The output of query( ) methods sometimes include integers
        and floats. 
        We convert them to strings. 
        It is up to the class to digest the output to treat them
        in a different way if needed.    

        And finally, we force all variables and values to be lower case
        """

        dict_attr = {}
        for attr in self.query_attributes:
            key = attr.lower()
            value = job_classad.get(attr, "undefined")
            value = str(value)
            value = value.lower() 
            dict_attr[key] = value
        return dict_attr


    def _sort(self):
        self.container.sort()


    def get(self):
        return self.container.get()


    def printable(self):
        """
        this method is just to get a printable version of the content
        being handle
    
        We calculate, the maximum lenght for each field 
        -in other words, each item at position i for each list-.
        Then we just double loop over the list of lists, 
        print each field, and the needed number of white spaces to 
        reach the maximum previously calculated for that field.
        That way, all fields are always displayed well aligned. 
        """

        matrix = self.get()

 
        if len(matrix) == 0:
            return ""
        
        # if there is actual content in the matrix...
    
        # 1. first we calculate the maximum lengths
        maxs = []
        for i in range(len(matrix[0])):
            # max length for field i on every line in out:
            max_i = max(len(line[i]) for line in matrix)
            maxs.append(max_i)
    
        # 2. then we double loop over the matrix 
    
        s = ""
        for line in matrix:
            for i in range(len(line)):
                s += "%s  " %line[i]
                s += " " * (maxs[i] - len(line[i]))
            s += '\n'
    
        s = s[:-1] # to remove the last \n
        return s





class condorq(CondorQuery):

    def __init__(self):

        # this is the list of HTCondor Job's ClassAds to query 
        self.query_attributes = ['ClusterId', 
                                'ProcId', 
                                'Owner', 
                                'QDate', 
                                'Cmd', 
                                'JobStatus', 
                                'EnteredCurrentStatus', 
                                'EC2AmiID', 
                                'MATCH_APF_QUEUE']

        super(condorq, self).__init__()


    def _query(self):
        schedd = htcondor.Schedd()
        self.out = schedd.query('true', self.query_attributes)

    def _store(self):
        for job_classad in self.out:
            dict_attr = self._clean(job_classad)
            new_item = Job(dict_attr)
            self.container.add(new_item)


class condorstatus(CondorQuery):

    def __init__(self):

        # this is the list of HTCondor startd's ClassAds to query 
        self.query_attributes = ['Name',
                                 'SlotID',
                                 'State',
                                 'Activity',
                                 'NodeType',
                                 'LoadAvg',
                                 'RemoteGroup',
                                 'EC2InstanceID',
                                 'EC2PublicDNS',
                                 'EC2AMIID',
                                 'SlotType']

        super(condorstatus, self).__init__()

    def _query(self):

        collector_name = htcondor.param.get('COLLECTOR_HOST')
        collector = htcondor.Collector(collector_name)
        self.out = collector.query(htcondor.AdTypes.Startd, "true", self.query_attributes)


    def _store(self):
        for job_classad in self.out:
            dict_attr = self._clean(job_classad)
            new_item = Slot(dict_attr)
            self.container.add(new_item)




class queuestatus(CondorQuery):

    def __init__(self):

        # this is the list of HTCondor Job's ClassAds to query 
        self.query_attributes = ['JobStatus',
                                 'MATCH_APF_QUEUE']

        super(queuestatus, self).__init__()


    def _query(self):
        schedd = htcondor.Schedd()
        queryout = schedd.query('true', self.query_attributes)

        # we now need to aggregate the output by queues
        self._aggregateinfo(queryout)


    def _aggregateinfo(self, queryout):

        status_mappings = {'0': 'unsub',
                           '1': 'idle',
                           '2': 'running',
                           '3': 'removed',
                           '4': 'completed',
                           '5': 'held',
                           '6': 'error'}

        emptydict = {'unsub'     : 0,
                     'idle'      : 0,
                     'running'   : 0,
                     'removed'   : 0,
                     'completed' : 0,
                     'held'      : 0,
                     'error'     : 0}

        queues = {}
        for job in queryout:
            if not 'MATCH_APF_QUEUE' in job.keys():
                # This job is not managed by APF. Ignore...
                continue
            apfqname = job['match_apf_queue']
            if apfqname not in queues.keys():
                queues[apfqname] = copy.copy(emptydict)

            jobstatus = str(job['jobstatus'])
            jobstatus = status_mappings[jobstatus]

            queues[apfqname][jobstatus] += 1

        # now we convert integers into strings 
        for k,v in queues.iteritems():
            for k2, v2 in v.iteritems():
                queues[k][k2] = str(v2)

        self.out = queues


    def _store(self):

        for qname in self.out.keys():
            dict_attr = self.out[qname] 
            dict_attr['qname'] = qname
            new_item = Queue(dict_attr)
            self.container.add(new_item)



# =============================================================================
#                        INFO TYPE CLASSES
# =============================================================================


class Container(object):
    """
    This class is just a container of objects.
    It is actually a completely abstract class
    so it can handle any kind of objects.

    NOTE: this is just legacy code, most probably it can be eliminated
    """

    def __init__(self):

        self.objs = []
        self.headers = []

    def add(self, obj):

        obj.container = self
        self.objs.append(obj)
        if not self.headers:
            # this is the first object being added
            self.headers = obj.list_attr

    def sort(self):
        """
        For this method to work, 
        the objects being stored are expected
        to have a method __cmp__( ) implemented
        """
        self.objs.sort()

    def get(self):
        out = []
        for obj in self.objs:
           out.append(obj.get())
        return out


class Item(object):

    def __init__(self, dict_attr):

        self.dict_attr = dict_attr

        self._create_attributes()
        self._format()


    def _format(self):
        raise NotImplementedError


    def __cmp__(self):
        raise NotImplementedError


    def _create_attributes(self):
        """ 
        add a class attribute for each item in self.dict_attr
        For example:

              self.clusterid = self.attr_dict['clusterId']
              self.procid = self.attr_dict['procid'] 
              self.owner = self.attr_dict['owner'] 
              Self.qdate = self.attr_dict['qdate'] 
              self.cmd = self.attr_dict['cmd'] 
              self.jobstatus = self.attr_dict['jobstatus']
              self.enteredcurrentstatus = self.attr_dict['enteredcurrentstatus'] 
              self.ec2amiid = self.attr_dict['ec2amiid'] 
              self.match_apf_queue = self.attr_dict['match_apf_queue']
              ...

        NOTE: this is not striclty needed.
              We can manage directly dict_attr dictionary, 
              but then the rest of the code is filled with stuff like
 
                 self.dict_attr[key] 

              instead of

                 self.key

              Using class attributes seems to be a little bit cleaner.
              That is the ONLY reason to do it this way.
        """ 
        for key, value in self.dict_attr.iteritems():
             setattr(self, key, value)


    def get(self):
        return [getattr(self,att) for att in self.list_attr]



class Job(Item):
    """
    This is the class to handle each Job.
    """

    def __init__(self, dict_attr):
        """
        attr_dict is each one of the objects returned by HTCondor query
        """

        # this is the list of attributes, or fields,  
        # we want to display in the output
        self.list_attr = ['id', 
                          'owner', 
                          'qdate', 
                          'cmd', 
                          'jobstatus', 
                          'enteredcurrentstatus', 
                          'ec2amiid', 
                          'match_apf_queue']
  
        super(Job, self).__init__(dict_attr)

    
    def _format(self):
        """
        in this method we manipulate the content 
        of the attr_dict input variables
        to build the final output with the format we want
        """

        self.id = '%s.%s' %(self.clusterid, self.procid)

        status_mappings = {'0': 'U', 
                           '1': 'I',
                           '2': 'R',
                           '3': 'X',
                           '4': 'C',
                           '5': 'H',
                           '6': 'E'}
        self.jobstatus = status_mappings[self.jobstatus]

        if self.jobstatus == 'R':
            self.timecurrentstatus = float(time.time()) - float(self.enteredcurrentstatus)
            self.timecurrentstatus = int(self.timecurrentstatus)
        else:
            self.timecurrentstatus = 0


        self.qdate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(self.qdate)))

        days = self.timecurrentstatus/(24*3600)
        rest = self.timecurrentstatus - days*24*3600
        m, s = divmod(int(rest), 60)
        h, m = divmod(m, 60)
        self.enteredcurrentstatus= '%d+%02d:%02d:%02d' %(days, h, m, s)


    def __cmp__(self, other):
        """
        to sort all jobs by id number
        """

        if self.id < other.id:
            return -1
        elif self.id > other.id:
            return 1
        else:
            return 0


class Slot(Item):
    """
    This is the class to handle each Slot
    """

    def __init__(self, dict_attr):
        """
        attr_dict is each one of the objects returned by HTCondor query
        """

        # this is the list of attributes, or fields,  
        # we want to display in the output
        self.list_attr = ['name',
                          'slotid',
                          'state',
                          'activity',
                          'nodetype',
                          'loadavg',
                          'remotegroup',
                          'ec2instanceid',
                          'ec2publicdns',
                          'ec2amiid']
  
        super(Slot, self).__init__(dict_attr)


    def _format(self):

        (slot, machine) = self.name.split("@")
        self.name = '%s:%s' %(machine, slot)
        if self.slottype == 'dynamic':
            self.name = '      %s' %self.name


    def __cmp__(self, other):
        """
        for the time being, we just leave things as they are
        """
        return 1








class Queue(Item):
    """
    This is the class to handle each Slot
    """

    def __init__(self, dict_attr):
        """
        attr_dict is each one of the objects returned by HTCondor query
        """

        # this is the list of attributes, or fields,  
        # we want to display in the output
        self.list_attr = ['qname',
                          'unsub', 
                          'idle',
                          'running',
                          'removed',
                          'completed',
                          'held',
                          'error']

        super(Queue, self).__init__(dict_attr)


    def _format(self):
        pass

    def __cmp__(self, other):
        """
        sort by queue name
        """

        if self.qname < other.qname:
            return -1
        elif self.qname > other.qname:
            return 1
        else:
            return 0


