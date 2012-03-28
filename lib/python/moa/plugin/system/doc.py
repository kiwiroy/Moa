# Copyright 2009-2011 Mark Fiers
# The New Zealand Institute for Plant & Food Research
# 
# This file is part of Moa - http://github.com/mfiers/Moa
# 
# Licensed under the GPL license (see 'COPYING')
# 
"""
**doc** - Manage job documentation
----------------------------------

Manage project / title / description for jobs

"""
import os
import getpass
import datetime
import subprocess

import moa.ui
import moa.utils
import moa.logger as l
from moa.sysConf import sysConf

def hook_prepare_3():
    job = sysConf['job']

    if not job.template.parameters.has_key('title'):
        job.template.parameters.title = {
            'optional' : False,
            'help' : 'A short and consise title for this job',
            'type' : 'string',
            'recursive' : False,
            }
    
    job.template.parameters.project = {
        'optional' : True,
        'help' : 'Project name',
        'type' : 'string'
        }

def hook_defineOptions():
    sysConf.parser.add_option(
        '-m', action='store',
        dest='message', help = 'Message accompanying this operations - ' + 
        'used for git & changelogs ')

def hook_defineCommands():
    """
    Set the moa commands for this plugin
    """
    sysConf['commands']['blog'] = {
        'desc' : 'Maintain a blog (blog.md)',
        'usage' : 'moa blog',
        'call' : blog,
        'needsJob' : False,
        'log' : True
        }
    sysConf['commands']['change'] = {
        'desc' : 'Maintain a changelog file (changelog.md)',
        'usage' : 'moa blog',
        'call' : change,
        'needsJob' : False,
        'log' : True
        }
    sysConf['commands']['readme'] = {
        'desc' : 'Edit the Readme.md file for this job',
        'usage' : 'moa readme',
        'call' : readme,
        'needsJob' : False,
        'log' : True
        }

def _readFromuser(job, header, fileName):
    """
    gather Blog or Changelog information
    """
    #moa.utils.moaDirOrExit(job)

    txt = []
    print header, "..."
    while True:
        try:
            line = raw_input("")
            txt.append(line)
        except (EOFError, KeyboardInterrupt):
            break

    sysConf.job.data.blog.txt = "\n".join(txt)

    try:
        with open(fileName) as F:
            oldFile = F.read()
    except IOError:
        oldFile = ""

    with open(fileName, "w") as F:
        now = datetime.datetime.now()
        header = "**%s - %s writes**" % (
            now.strftime("On %A, %d %b %Y %H:%M"), getpass.getuser()) 
        F.write("%s\n\n" %  header)
        F.write("\n    ".join(txt))
        F.write("\n-----\n")
        F.write(oldFile)

def blog(job):
    """
    Allows a user to maintain a blog for this job (in Blog.md).

    Use it as follows::

        $ moa blog
        Enter your blog message (ctrl-d on an empty line to finish)

        ... enter your message here ..
        
        [ctrl-d]

    Note: the ctrl-d needs to be given on an empty line. The text is
    appended to moa.desciption. In the web interface this is converted
    to Markdown_.

    .. _Markdown: http://daringfireball.net/projects/markdown/ markdown.
    """
    _readFromuser(
        job, 
        header="enter your blog message (ctrl-d on an empty line to finish)",
        fileName="Blog.md")
                  
def change(job):
    """
    Allows a user to enter a short note that is appended to
    Changelog.md (including a timestamp). Use it as follows::

        $ moa change
        Enter your changelog message (ctrl-d on an empty line to finish)

        ... enter your message here ..
        
        [ctrl-d]

    Note: the ctrl-d needs to be given on an empty line. The text is
    appended to moa.desciption. In the web interface this is converted
    to Markdown_.

    .. _Markdown: http://daringfireball.net/projects/markdown/ markdown.
    """
    _readFromuser(
        job, 
        header="Enter your changelog message (ctrl-d on an empty line to finish)",
        fileName="Changelog.md")
                  

def readme(job):
    """
    Edit the Readme.md file - you could, obviously, also edit the file yourself.
    """
    
    subprocess.call([os.environ.get('EDITOR','nano'), 'Readme.md'])



def _update_git(filename):
    """
    Check if a file is under version control & commit changes    
    """
    job = sysConf.job
    if not sysConf.git.repo:
        #repo is not initalized..(not in a repository?)
        return
    
    if os.path.exists(filename):    
        sysConf.git.repo.index.add([filename])
        sysConf.git.commitJob(job, 'Worked on %s in  %s' % (filename, job.wd))
        
    
def hook_git_finish_readme():
    """
    Execute just after setting running moa readme
    """
    _update_git('Readme.md')

def hook_git_finish_blog():
    """
    Execute just after setting running moa blog
    """
    _update_git('Blog.md')


def hook_git_finish_change():
    """
    Execute just after setting running moa blog
    """
    _update_git('Changelog.md')
