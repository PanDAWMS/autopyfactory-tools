#!/bin/env python

from autopyfactory_tools.lib.querylib import condorstatus

import argparse

parser = argparse.ArgumentParser(description='Prints information about the condor slots')
parser.add_argument("-H", "--headers", help="Prints the header of each column", action="store_true")
args = parser.parse_args()




cs = condorstatus(args)
cs.run()
print cs.printable()

