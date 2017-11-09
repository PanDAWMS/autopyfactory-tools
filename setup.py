#!/usr/bin/env python
#
# Setup prog for autopyfactory-tools
#
#

release_version='1.0.3'

import commands
import os
import re
import sys

from distutils.core import setup
from distutils.command.install import install as install_org
from distutils.command.install_data import install_data as install_data_org

## Python version check. 
#major, minor, release, st, num = sys.version_info
#if major == 2:
#    if not minor >= 4:
#        print("Autopyfactory requires Python >= 2.4. Exitting.")
#        sys.exit(0)

# ===========================================================
#                D A T A     F I L E S 
# ===========================================================



# etc files are handled by setup.cfg
etc_files = [ ]


sbin_scripts = ['sbin/apf-condor-q',
                'sbin/apf-condor-status',
                'sbin/apf-queue-status',
                'sbin/apf-reverse-logstree',
                'sbin/apf-simulate-scheds',
               ]

# -----------------------------------------------------------

rpm_data_files=[('/usr/sbin', sbin_scripts),]
home_data_files=[]


# -----------------------------------------------------------

def choose_data_files():
    rpminstall = False
     
    if 'bdist_rpm' in sys.argv:
        rpminstall = True

    elif 'install' in sys.argv:
        for a in sys.argv:
            if a.lower().startswith('--home'):
                rpminstall = False
                userinstall = True
                
    if rpminstall:
        return rpm_data_files
    else:
        return home_data_files
       
# ===========================================================

# setup for distutils
setup(
    name="autopyfactory-tools",
    version=release_version,
    description='autopyfactory-tools package',
    long_description='''This package contains autopyfactory utils''',
    license='GPL',
    author='APF Team',
    author_email='autopyfactory-l@lists.bnl.gov',
    maintainer='Jose Caballero',
    maintainer_email='jcaballero@bnl.gov',
    url='https://twiki.cern.ch/twiki/bin/view/Atlas/PanDA',
    packages=['autopyfactory_tools',
              'autopyfactory_tools.bin',
              'autopyfactory_tools.lib',
             ],

    
    data_files = choose_data_files()
)
