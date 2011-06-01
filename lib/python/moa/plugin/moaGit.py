# Copyright 2009-2011 Mark Fiers
# The New Zealand Institute for Plant & Food Research
# 
# This file is part of Moa - http://github.com/mfiers/Moa
# 
# Licensed under the GPL license (see 'COPYING')
# 
"""
**moaGit** - maintain a git repository with job information
-----------------------------------------------------------

"""
import os
import sys
import git 
import time
import optparse

from moa.sysConf import sysConf
import moa.logger as l
import moa.plugin.newjob

def hook_defineCommands():
    sysConf['commands']['history'] = {
        'desc' : 'display a version control log',
        'call': gitlog
        }
    sysConf['commands']['tag'] = {
        'desc' : 'Tag the current version',
        'call': tag
        }
    
def hook_defineOptions():
    parserG = optparse.OptionGroup(
        sysConf['parser'], 'Version control (Git)')
    parserG.add_option('--m', action='store',
                       dest='gitMessage', 
                      help = 'Commit message for git')
    
    sysConf.parser.add_option_group(parserG)

def _getRepo(job):
    """
    Return the git repository object
    """
    wd = job.wd
    try:
        return git.Repo(wd)
    except git.InvalidGitRepositoryError:
        return None

def _commit(job, message):
    repo = _getRepo(job)
    if not repo:
        if sysConf.plugin_settings.moaGit.warnings:
            moa.ui.message("git plugin is active, but no repository found")
        return
        
    l.debug("Found git repo: Commiting")
    repo.index.add(job.getFiles())
    repo.index.commit(message)

    
def tag(job):
    repo = _getRepo(job)
    if not repo:
        moa.ui.exitError("Not inside a git repository")
        return

    tagname = sysConf.args[1]
    message = sysConf.options.gitMessage
    l.info('tagging with "%s"' % tagname)
    repo.create_tag(tagname, message=message)

def hook_postSet():
    """
    Execute just after setting a parameter
    """
    job = sysConf.job
    _commit(job, 'moa set %s in %s' % (
        " ".join(sysConf['newargs']), job.wd))
    
def hook_postNew():
    """
    To be executed just after the 'moa new' command
    """    
    job = sysConf.job
    _commit(job, "created job %s in %s" % (job.template.name, job.wd))

def gitlog(job):
    """
    Print a log to screen
    """
    repo = _getRepo(job)
    if not repo:
        l.info("noting to report - no git repository found")
        return

    tags = {}
    
    for t in repo.tags:
        tags[t.commit] = t

    for c in repo.iter_commits():
        #if str(c) in tags.keys()
        t = time.strftime("%d %b %Y %H:%M", time.localtime(c.authored_date))

        if c in tags.keys():
            print " tag| %s" % tags[c]
        
        print "%3s | %s | %s" % (c.count(), t, c.message)
