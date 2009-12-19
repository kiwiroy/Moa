#!/usr/bin/env python
# 
# Copyright 2009 Mark Fiers, Plant & Food Research
# 
# This file is part of Moa - http://github.com/mfiers/Moa
# 
# Moa is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your
# option) any later version.
# 
# Moa is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Moa.  If not, see <http://www.gnu.org/licenses/>.
# 
"""
moa wrapper for the API 
"""

import os
import sys

import optparse
import subprocess

from  moa.logger import l
from moa import utils

#moa specific libs - first prepare for loading libs
if not os.environ.has_key('MOABASE'):
    raise Exception("MOABASE is undefined")

#process the .pth file in the $MOABASE/bin folder !
site.addsitedir(os.path.join(os.environ['MOABASE'], 'lib', 'python'))

MOABASE = os.environ["MOABASE"]
TEMPLATEDIR = os.path.join(MOABASE, 'template')

##
## Read the moa configutation file 
ETC = {}
for line in open(os.path.join(MOABASE, 'etc', 'moa.conf.mk')).readlines():
    line = line.strip()
    if not line: 
        continue
    if line[0] == '#': 
        continue
    ls = [x.strip() for x in line.split('=', 1)]
    if len(ls) == 2:
        ETC[ls[0]] = ls[1]

def _startMake(d, args, verbose = True,
               pipeOut = subprocess.PIPE,
               pipeErr = subprocess.PIPE):
    """
    A function to run Make in a certain directory d with specific args
    """
    if type(args) == type("str"):
        args = [args]
        
    if not verbose:
        args.append('-s')
        
    p = subprocess.Popen(
        ["make"] + args,
        shell=False,
        cwd = d,
        stdout = pipeOut,
        stderr = pipeErr)
    return p

def runMake(directory = None, args = [], verbose=True,
            catchout=False):
    """
    Complete a make run
    """
    if not directory: directory = os.getcwd()
    if type(args) == type('hi'): args = [args]
    l.debug('Starting "make %s" in %s' % (" ".join(args), directory))

    if catchout:
        outpipe = subprocess.PIPE
        errpipe = subprocess.PIPE
    else:
        outpipe = None
        errpipe = None
    
    p = _startMake(directory, args, verbose=verbose,
                   pipeOut=outpipe, pipeErr = errpipe)
    (out, err) = p.communicate()
    rc = p.returncode
    l.debug("Finished make in %s with return code %s" % (directory, rc))
    return rc, out, err

def runMakeAndExit(directory = None, verbose=True, args = []):
    """
    Convenience function - run, report & exit
    """
    l.debug("ji %s %s" % (directory, args))
    rc, out, err = runMake(directory=directory, verbose=verbose, args=args)
    utils.exit(rc)

##
## API Command Dispatcher
## 

def execute(d, args = []):
    """
    Execute 'make' in directory d
    """
    _startMake(d, args)