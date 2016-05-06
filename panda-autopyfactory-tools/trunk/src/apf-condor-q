#!/bin/env python

from apftoolslib import condorq

import argparse

parser = argparse.ArgumentParser(description='Prints information about the current pilots')
parser.add_argument("-H", "--headers", help="Prints the header of each column", action="store_true")
args = parser.parse_args()


cq = condorq(args)
cq.run()
print cq.printable()

