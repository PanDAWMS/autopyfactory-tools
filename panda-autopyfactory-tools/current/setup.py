#!/usr/bin/env python
#
# Setup prog for autopyfactory
#
#

release_version='1.0.0'

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


utils_files = ['src/apf-agis-config',
               'src/apf-queue-status',
               'src/apf-queue-jobs-by-status.sh',
               'src/apf-test-pandaclient',
               'src/apf-check-old-pilots',
               'src/apf-search-failed',
               'src/apf-simulate-scheds',
               ]

etc_files = ['etc/apf-agis-config-template.conf-example',
            ]



# -----------------------------------------------------------

rpm_data_files=[('/usr/share/apf',     utils_files),                                        
                ('/etc/apf',           etc_files),
               ]

# -----------------------------------------------------------

def choose_data_files():
    rpminstall = True
    userinstall = False
     
    if 'bdist_rpm' in sys.argv:
        rpminstall = True

    elif 'install' in sys.argv:
        for a in sys.argv:
            if a.lower().startswith('--home'):
                rpminstall = False
                userinstall = True
                
    if rpminstall:
        return rpm_data_files
    elif userinstall:
        return home_data_files
    else:
        # Something probably went wrong, so punt
        return rpm_data_files
       
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
    packages=[ ],
    scripts = [ ],
    
    data_files = choose_data_files()
)
