import os
import sys
import site

# one directory above the project, so project name will be needed for imports
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# path to the virtualenv
venv_path = os.path.abspath(os.path.join(root_dir, '..', 'minddrag-django-env'))

# with mod_wsgi >= 2.4, this line will add this path in front of the python path
site.addsitedir(os.path.join(venv_path, 'lib/python2.6/site-packages'))

# add dir above this django project
sys.path.append(root_dir)

# add this django project
# (so we don't need the project name in import statements)
sys.path.append(os.path.join(root_dir, 'minddrag'))
 
os.environ['DJANGO_SETTINGS_MODULE'] = 'minddrag.settings'
  
import django.core.handlers.wsgi
   
application = django.core.handlers.wsgi.WSGIHandler()

