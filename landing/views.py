__author__ = 'jblowe'

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings

from cspace_django_site.main import cspace_django_site
from common import cspace

config = cspace_django_site.getConfig()
hostname = cspace.getConfigOptionWithSection(config,
                                             cspace.CONFIGSECTION_AUTHN_CONNECT,
                                             cspace.CSPACE_HOSTNAME_PROPERTY)

TITLE = 'Applications Available'

hiddenApps = 'hello service suggest suggestsolr suggestpostgres solarapi imageserver landing'.split(' ')
loginRequiredApps = 'ireports imagebrowser imaginator search uploadmedia locviewer'.split(' ')

#@login_required()
def index(request):
    config = cspace_django_site.getConfig()
    appList = [app for app in settings.INSTALLED_APPS if not "django" in app and not app in hiddenApps]
    
    if not request.user.is_authenticated():
        appList = [app for app in appList if not app in loginRequiredApps]
    
    appList.sort()
    return render(request, 'listApps.html', {'appList': appList, 'labels': 'name file'.split(' '), 'title': TITLE, 'hostname': hostname})
