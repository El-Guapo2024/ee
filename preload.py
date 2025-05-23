# preload.py at each level defines special variables and/or functions to be
# inherited by pages farther down the tree.

# LOOK AND FEEL

cs_base_color = "#A31F34"  # the base color
cs_header = 'MITFE'  # the upper-left corner
cs_icon_url = 'COURSE/favicon_local.gif'  # the favicon, if any
# the 'header' text for the page
cs_long_name = cs_content_header = "MIT Fundamentos de Electronica"
cs_title = 'MIT Fundamentos de Electronica'  # the browser's title bar

# don't try to parse markdown inside of these tags
cs_markdown_ignore_tags = ('script', 'svg', 'textarea')

# defines the menu at the top of the page in the default template.
# each dictionary defines one menu item and should contain two keys:
#  * text: the text to show for the link
#  * link: the target of the link (either a URL or another list of this same form)
cs_top_menu = [
    {'link': 'COURSE', 'text': 'Homepage'},
    {'text': 'Course', 'link': 
        [
            {'text': 'Laboratorio 0', 'link': 'COURSE/part_1/laboratorio_0'},
        ]
    }
]


# AUTHENTICATION

cs_auth_type='login'  # use the default (username/password based) authentication method
# for actually running a course at MIT, I like using OpenID Connect instead (https://oidc.mit.edu/).

# custom XML tag handling, copied from one i wrote for 6.01 ages ago.  can
# probably largely be ignored (or can be updated to handle other kinds of
# tags).
import re
import hashlib
import subprocess
import shutil
def environment_matcher(tag):
    return re.compile("""<%s>(?P<body>.*?)</%s>""" % (tag, tag), re.MULTILINE|re.DOTALL)
def cs_course_handle_custom_tags(text):
    # CHECKOFFS AND CHECK YOURSELFS
    checkoffs = 0
    def docheckoff(match):
        nonlocal checkoffs
        d = match.groupdict()
        checkoffs += 1
        return '<div class="checkoff"><b>Checkoff %d:</b><p>%s</p><p><span id="queue_checkoff_%d"></span></p></div>' % (checkoffs, d['body'], checkoffs)
    text=re.sub(environment_matcher('checkoff'), docheckoff, text)

    checkyourself = 0
    def docheckyourself(match):
        nonlocal checkyourself
        d = match.groupdict()
        checkyourself += 1
        return '<div class="question"><b>Check Yourself %d:</b><p>%s</p><p><span id="queue_checkyourself_%d"></span></p></div>' % (checkyourself, d['body'], checkyourself)
    text=re.sub(environment_matcher('checkyourself'), docheckyourself, text)

    return text


# PYTHON SANDBOX

csq_python3 = True
csq_python_sandbox = "python"
# something like the following can be used to use a sandboxed python
# interpreter on the production copy (after following the directions at
# https://catsoop.mit.edu/website/docs/installing/server_configuration for
# setting up the sandbox):
#
#if 'localhost' in cs_url_root:
#    # locally, just use the system Python install
#    csq_python_sandbox_interpreter = '/usr/bin/python3'
#else:
#    # on the server, use the properly sandboxed python
#    csq_python_sandbox_interpreter = '/home/ubuntu/py3_sandbox/bin/python3'


# PERMISSIONS

# users' roles are determined by the files in the __USERS__ directory.  each
# has the form username.py other information (such as a section number, if
# relevant) can be stored there as well but the system will look for role =
# "Student" or similar, and use that to set the user's permissions.
#
#  view: allowed to view the contents of a page
#  submit: allowed to submit to a page
#  view_all: always allowed to view every page, regardless of when it releases
#  submit_all: always allowed to submit to every question, regardless of when it releases or is due
#  impersonate: allowed to view the page "as" someone else
#  admin: administrative tasks (such as modifying group assignments)
#  whdw: allowed to see "WHDW" page (Who Has Done What)
#  email: allowed to send e-mail through CAT-SOOP
#  grade: allowed to submit grades
cs_default_role = 'Guest'
cs_permissions = {'Admin': ['view_all', 'submit_all', 'impersonate', 'admin', 'whdw', 'email', 'grade'],
               'Instructor': ['view_all', 'submit_all', 'impersonate', 'admin', 'whdw', 'email', 'grade'],
               'TA': ['view_all', 'submit_all', 'impersonate', 'whdw', 'email', 'grade'],
               'UTA': ['view_all', 'submit_all', 'impersonate', 'grade'],
               'LA': ['view_all', 'submit_all','impersonate', 'grade'],
               'Student': ['view', 'submit'],
               'Guest': ['view', 'submit']}


# TIMING

# release and due dates can always be specified in absolute terms:
#   "YYYY-MM-DD:HH:MM"
# the following allows the use of relative times (and/or per-section times)
# section_times maps section names to times (below, the default section has
# lecture at 8am on Tuesdays)
# this allows setting, e.g.,  cs_release_date = "lec:2" to mean "release this
# at lecture time in week 2"
# different sections will get different times if they are specified below.
# adding section = 2, for example, to someone's __USERS__ file will cause the
# system to look up the key 2 in the dictionary below.
cs_first_monday = '2017-02-06:00:00'
section_times = {'default': {'lec': 'T:08:00', 'lab': 'T:09:00', 'lab_due':'M+:22:00', 'soln':'S+:08:00', 'tut':'W:08:00'},

}

def cs_realize_time(meta, rel):
    try:
        start, end = rel.split(':')
        section = cs_user_info.get('section', 'default')
        rel = section_times.get(section, {}).get(start, section_times['default'].get(start, 'NEVER'))
        meta['cs_week_number'] = int(end)
    except:
        pass
    return csm_time.realize_time(meta,rel)

import time
from datetime import datetime

# cs_post_load is invoked after the page is loaded but before it is rendered.
# the example below shows the time at which the current page was last modified
# (based on the Git history).
def cs_post_load(context):
    if 'cs_long_name' in context:
        context['cs_content_header'] = context['cs_long_name']
        context['cs_title'] = '%s | %s' % (context['cs_long_name'], context['cs_title'])
    try:
        loc = os.path.abspath(os.path.join(context['cs_data_root'], 'courses', *context['cs_path_info']))
        git_info = subprocess.check_output(["git", "log", "--pretty=format:%h %ct",
                                            "-n1", "--", "content.catsoop",
                                            "content.md", "content.xml",
                                            "content.py"], cwd=loc)
        h, t = git_info.split()
        t = context['csm_time'].long_timestamp(datetime.fromtimestamp(float(t))).replace(';', ' at')
        context['cs_footer'] = 'This page was last updated on %s (revision <code>%s</code>).<br/>&nbsp;<br/>' % (t, h.decode())
    except:
        pass
