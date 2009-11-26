import os.path
import sys

sys.path.append("../private/")
import WWWMoaXML


def is_tcp_port_available(port):
    return True

def get_cgi_handler_path():
    return "/usr/bin/python"

def get_install_path():
    return os.path.abspath("../public")

def escape_string(str):
    return str # [!] Placeholder

def get_env_file(path):
    return """<?xml version=\"1.0\"?>

<env>

    <!-- This configuration file was auto-generated by the WWWMoaLighty utility. -->

    <content path=\"""" + WWWMoaXML.fix_text(path) +"""\" />

</env>

"""


def get_config_file(port):
    return """

###         CONFIGURATION FILE FOR lighttpd         ###
### This file was auto-generated by the             ###
### WWWMoaLighty utility. Generally, it is          ###
### suggested that you not tinker with it unless    ###
### you are an advanced user.  Also note that       ###
### the aforementioned utility might remove this    ###
### file upon certain events, so you might want to  ###
### save a copy of it at another location if you    ###
### are interested in modifying it.                 ###


## User Specified Parameters ##
server.port=""" + str(port) + """


## Install Specific Information ##

server.document-root=\"""" + escape_string(get_install_path()) + """\"

cgi.assign=(
\".py\" => \"""" + escape_string(get_cgi_handler_path()) +"""\"
)


## Required lighttpd Modules ##

server.modules=(
\"mod_cgi\",
\"mod_rewrite\"
)


## MIME Type Dictionary ##

mimetype.assign=(
\".html\" => \"text/html\",
\".htm\" => \"text/html\",
\".txt\" => \"text/plain\",
\".css\" => \"text/css\",
\".js\" => \"text/javascript\",
\".png\" => \"image/png\",
\".gif\" => \"image/gif\",
\".jpg\" => \"image/jpeg\",
\".jpeg\" => \"image/jpeg\"
)


## WWWMoa Specific Parameters ##

server.error-handler-404=\"/error-nf.py\"

index-file.names=(
\"index.py\"
)

url.rewrite-once=(
\"^/index$\" => \"/index.py\",
\"^/help$\" => \"/help.py\",
\"^/moa$\" => \"/moa.py\",
\"^/moa/(.*)$\" => \"/moa.py?request=$1\"
)


"""
