class UI(object):
    """

    this class just implements a method to print out to the stdout 
    the final results

    It simply gets the output of the query, after being interpreted and 
    manipulated, by calling method get( )
    This class does not implement method get( ), 
    so get( ) it is supposed to be implemented in a different class XYZ,
    and everything being used by a child class:

        class Child(XYZ, UI)

    therefore, class Child will have available methods from this class UI
    and from class XYZ that implements get( ), among other things.
    """


    def display(self):
        """

        this is the method that prints out to stdout the results
        of the query.

        We first call get( ), which is implemented in a different class.
        The output of get MUST be a list of lists.
        We calculate, the maximum lenght for each field 
        -in other words, each item at position i for each list-.
        Then we just double loop over the list of lists, 
        print each field, and the needed number of white spaces to 
        reach the maximum previously calculated for that field.
        That way, all fields are always displayed well aligned. 
        """


    out = self.get()

        if len(out) == 0:
            return ""
        
        # if there is actual content in out...
        maxs = self._calculate_max(out)
        self._display(out, maxs)
 

    def _calculate_max(self, out):

        maxs = []
        for i in range(len(out[0])):
            # max length for field i on every line in out:
            max_i = max(len(obj[i]) for obj in out)
            maxs.append(max_i)
        return maxs


    def _display(self, out, maxs):

        for line in out:
            s = ""
            for i in range(len(line)):
                s += "%s  " %line[i]
                s += " " * (maxs[i] - len(line[i]) )
            print s



class Container(object):
    """

    This class is just a container of objects.
    It is actually a completely abstract class
    so it can handle any kind of objects.
    """


    def __init__(self):

        self.objs = []


    def add(self, obj):

        obj.container = self
        self.objs.append(obj)


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

    ###def __str__(self):
    ###    s = ''
    ###    for obj in self.objs:
    ###        s += obj.__str__()
    ###    if len(s)>0:
    ###        # this is to remove the very last \n
    ###        s = s[:-1]
    ###    return s


        """
        """
    """
    """
        """
        """
    """
    """
