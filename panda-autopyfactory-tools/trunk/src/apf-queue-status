#!/bin/env python

import argparse
from apftoolslib import queuestatus


parser = argparse.ArgumentParser(description='Prints aggregated status info queue by queue')
parser.add_argument("-N", "--new", help="Makes the output to be displayed in new format", action="store_true")
parser.add_argument("-H", "--headers", help="Prints the header of each column. Triggers the new output format.", action="store_true")
parser.add_argument("-L", "--longest", help="Prints two additional columns with the longest waiting and running times. Triggers the new output format.", action="store_true")
args = parser.parse_args()

if args.headers or args.longest:
    args.__dict__['new'] = True


qs = queuestatus(args)
qs.run()
print qs.printable()

