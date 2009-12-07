import os
import os.path
import sys
import wwwmoa.info.moa as moainfo

import wwwmoa.formats.xml as xml


def get_cgi_handler_path():
    return sys.executable # gets the pathname of the Python interpreter, which we will use for CGI

def get_install_static_path():
    return os.path.normpath(os.path.join(moainfo.get_base(),"www/static"))

def get_install_dynamic_path():
    return os.path.normpath(os.path.join(moainfo.get_base(),"www/dynamic"))

def get_install_moabase_bin_path():
    return os.path.normpath(os.path.join(moainfo.get_base(),"bin"))

def get_install_moabase_path():
    return moainfo.get_base()

def get_path_variable():
    if "PATH" in os.environ:
        if os.environ["PATH"]!="":
            return os.environ["PATH"]+os.pathsep+get_install_moabase_bin_path()

    return get_install_moabase_bin_path()

def escape_string(str):
    return str # [!] Placeholder

def get_env_file(home):
    return """<?xml version=\"1.0\"?>

<env>

    <!-- This configuration file was auto-generated by the WWWMoaLighty utility. -->

    <content path=\"""" + xml.fix_text(home) +"""\" />

</env>

"""

def port_has_env(port):
    return os.access(get_env_file_path(port), os.F_OK)

def get_config_file(port, home):
    return """

################################################################
###             CONFIGURATION FILE FOR lighttpd              ###
### This file was auto-generated by the WWWMoaLighty utility.###
### Generally, it is suggested that you not tinker with it   ###
### unless you are an advanced user.                         ###
################################################################


## User Specified Parameters ##

server.port=""" + str(port) + """


## Install Specific Information ##

server.document-root=\"""" + escape_string(get_install_static_path()) + """\"

cgi.assign=(
    \".py\" => \"""" + escape_string(get_cgi_handler_path()) +"""\"
)


## Required lighttpd Modules ##

server.modules=(
    \"mod_expire\",
    \"mod_cgi\",
    \"mod_rewrite\",
    \"mod_alias\",
    \"mod_setenv\"
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
    \".jpeg\" => \"image/jpeg\",
    \".pdf\" => \"application/pdf\",
    \".svg\" => \"image/svg+xml\"
)


## WWWMoa Specific Parameters ##

server.error-handler-404=\"/error-nf.html\"

index-file.names=(
    \"index.html\"
)

$HTTP[\"url\"]=~\"^/direct($|(/.*))\" {
    dir-listing.active=\"enable\"
}



url.rewrite-once=(
    \"^/api$\" => \"/dynamic/api.py?\",
    \"^/api/([^\\\\?]*)$\" => \"/dynamic/api.py?$1\",
    \"^/api/(([^\\\\?]*)\\\\?(.*))$\" => \"/dynamic/api.py?$1\",
    \"^/index$\" => \"/index.html\",
    \"^/images/([^\\\\.]*)$\" => \"/images/$1.png\",
    \"^/styles/([^\\\\.]*)$\" => \"/styles/$1.css\",
    \"^/scripts/([^\\\\.]*)$\" => \"/scripts/$1.js\",
    \"^/about$\" => \"/dynamic/redir.py?target=about\",
    \"^/go/moa$\" => \"/dynamic/redir.py?target=moa\",
    \"^/go/firefox$\" => \"/dynamic/redir.py?target=firefox\",
    \"^/go/python$\" => \"/dynamic/redir.py?target=python\",
    \"^/go/dojo$\" => \"/dynamic/redir.py?target=dojo\"
)

alias.url=(
    \"/dynamic\" => \""""+escape_string(get_install_dynamic_path())+"""\",
    \"/direct\" => \""""+escape_string(home)+"""\"
)

expire.url=(
    \"/\" => \"access 0 seconds\"
)

setenv.add-environment+=(
    \"MOABASE\" => \""""+escape_string(get_install_moabase_path())+"""\",
    \"PATH\" => \""""+escape_string(get_path_variable())+"""\"
)

################################################################

"""

