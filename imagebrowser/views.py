__author__ = 'jblowe'

import os
import re
import time

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response

from common.utils import doSearch, setConstants, loginfo
from common import cspace  # we use the config file reading function
from cspace_django_site import settings
from os import path

config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), 'imagebrowser')

MAXMARKERS = int(config.get('imagebrowser', 'MAXMARKERS'))
MAXRESULTS = int(config.get('imagebrowser', 'MAXRESULTS'))
MAXLONGRESULTS = int(config.get('imagebrowser', 'MAXLONGRESULTS'))
SOLRSERVER = config.get('imagebrowser', 'SOLRSERVER')
SOLRCORE = config.get('imagebrowser', 'SOLRCORE')
TITLE = config.get('imagebrowser', 'TITLE')
#SUGGESTIONS = config.get('imagebrowser', 'SUGGESTIONS')
#LAYOUT = config.get('imagebrowser', 'LAYOUT')

from common import cspace
from cspace_django_site.main import cspace_django_site

config = cspace_django_site.getConfig()


@login_required()
def images(request):
    if request.method == 'GET' and request.GET != {}:
        context = {'searchValues': request.GET}

        context = setConstants(context)

        context['text'] = request.GET['text']
        #context['pgNum'] = pgNum if 'pgNum' in context else '1'
        #context['url'] = url
        context['displayType'] = 'list'
        context['pixonly'] = 'true'
        context['title'] = TITLE

        # do search
        loginfo('start search', context, request)
        context = doSearch(context)

        return render(request, 'showImages.html', context)

    else:
        return render(request, 'showImages.html',
                      {'title': TITLE, 'pgNum': 10, 'maxresults': 20})
