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
Adhoc - some utilities to quickly create adhoc jobs
"""

import os
import re
import sys
import optparse

import moa.job
import moa.logger
import moa.plugin
l = moa.logger.l

def _sourceOrTarget(g):
    """
    Determine if this glob is a likely source or
    target, depending on where the output is aimed to go
    """
    d = g.groups()[0]
    if not d: return 'target'
    if d[:2] == './': return 'target'

    if d[:2] == '..': return 'source'
    if d[0] == '/': return 'source'
    return 'target'

def defineCommands(data):
    data['commands']['adhoc'] = { 
        'desc' : 'Quickly create an adhoc analysis',
        'call' : createAdhoc
        }

def defineOptions(data):
    parserN = optparse.OptionGroup(data['parser'], "Moa adhoc (a)")
    data['parser'].set_defaults(directory=".")
    try:
        parserN.add_option("-t", "--title", dest="title", help="Job title")
        parserN.add_option("-d", "--directory", 
                           dest="directory",
                           help="Directory to create the new template in (default: .)")
    except optparse.OptionConflictError:
        pass # these options are probably already defined in the newjob plugin
    
    parserN.add_option("-m", "--mode",
                       dest="mode",
                       help="Adhoc mode to run (omit for an educated guess)")
    data['parser'].add_option_group(parserN)


def createAdhoc(data):
    """
    Create an adhoc job
    """

    wd = data['cwd']
    options = data['options']
    args = data['newargs']

    command = " ".join(args).strip()
    
    if not command:
        command=moa.utils.askUser('adhoc_command=', '')

    l.info('Parsing command: %s' % command)
    params = []
    mode = None
    searchGlobs = True
        
    if options.mode:
        mode = options.mode
        if options.mode == 'simple': searchGlobs = False
        if not options.mode in ['seq', 'par', 'all', 'simple']:
            l.critical("Unknown adhoc mode: %s" % options.mode)
            sys.exit(-1)
    elif '$<' in command:
        mode = 'seq'
        searchGlobs = False
    elif ('$^' in command) or ('$?' in command):
        mode = 'all'
        searchGlobs = False
        l.warn("Observed '$^' or '$?', setting mode to 'all'")
        l.warn("Processing all files in one go")

    #see if we have to look for file globs
    if not searchGlobs:
        l.info("No recognizable globs found")
    else:
        #it appears to make sens to see if there is a glob in the command
        #reFindGlob = re.compile(r"^(.*)\s+([^ *?]+" +
        #                        os.sep +
        #                        r")([^ *]*\*[^ *]*?)((?:\.[^ .*]+)?)\s+(.*)$")
        refindGlob = re.compile(r"([^ *]+" + os.sep + ")?([^ *]*\*[^ *]*?)((?:\.[^ .*]+)?)")
        globs = []
        for g in refindGlob.finditer(command):
            globs.append(g)

        if globs:
            globReplace = '$<', '$t'                                
            mode = 'seq'
            if len(globs) > 2:
                raise Exception("Too many globs ??  I not understand :(")
            if len(globs) == 2:
                st1 = _sourceOrTarget(globs[0])
                st2 = _sourceOrTarget(globs[1])
                if st1 == st2:
                    l.warn("Unsure wich is the source &  target glob, assuming:")
                    inGlob,outGlob = globs
                if st1 == 'source': inGlob,outGlob = globs
                else:
                    outGlob,inGlob = globs
                    globReplace = '$t', '$<'
                    
                l.info("Input glob: %s" % inGlob.group())
                l.info("Output glob: %s" % outGlob.group())
            else:
                l.info("Input glob: %s" % globs[0].group())
                inGlob, outGlob = globs[0], None

            inD, inG, inE = inGlob.groups()
            if not inD: inD = ""
            if not inE: inE = ""
            l.info(" - set input dir        : %s" % inD)
            l.info(" - set input glob       : %s" % inG)
            l.info(" - set input extension  : %s" % inE[1:])

            params += ['adhoc_input_dir=%s' % inD]
            params += ['adhoc_input_glob=%s' % inG]
            params += ['adhoc_input_extension=%s' % inE[1:]]

            if outGlob:
                ouD, ouG, ouE = outGlob.groups()
                if not ouD: ouD = ""
                if not ouE: ouE = ""
                ogg = outGlob.groups()

                ouG1, ouG2 = ouG.split('*')
                sed = r"s^\(.*\)%s^%s%s\1%s%s^g" % (
                    inE.replace('.', '\.'),
                    ouD.replace('/', '/'),
                    ouG.split('*')[0],
                    ouG.split('*')[1],
                    ouE
                    )
                l.info(" - set name_sed         : %s " % sed)
                l.info(" - set output dir       : %s " % ouD)
                params += ['adhoc_output_dir=%s' % ouD]
                params += ['adhoc_name_sed=%s' % sed]

            #hack the commandline
            for i in range(len(globs)-1, -1, -1):
                g = globs[i]
                command = command[:g.start()] + globReplace[i] + command[g.end():]

    if not mode:
        mode = 'simple'

    if command:
        l.info(" - set command          : %s" % command)
        params.append('adhoc_process=%s' % command)

    l.info(" - set mode             : %s" % mode)

    if mode == 'seq':
        l.warn("Note: adhoc is running in sequential ('seq') mode. If ")
        l.warn("you are confident that jobs do not interfere, you might ")
        l.warn("consider setting adhoc to parallel operation:")
        l.warn("$ set adhoc_mode=par")
               


    l.debug('setting parameters %s' % params)
    moa.job.newJob(template='adhoc',
                   wd = wd,
                   title = options.title,
                   force = options.force,
                   parameters=params)


        
