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
from operator import itemgetter

config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), 'locviewer')

connect_string = config.get('connect', 'connect_string')

MAXMARKERS = int(config.get('locviewer', 'MAXMARKERS'))
MAXRESULTS = int(config.get('locviewer', 'MAXRESULTS'))
MAXLONGRESULTS = int(config.get('locviewer', 'MAXLONGRESULTS'))
IMAGESERVER = config.get('locviewer', 'IMAGESERVER')
# CSPACESERVER = config.get('locviewer', 'CSPACESERVER')
SOLRSERVER = config.get('locviewer', 'SOLRSERVER')
SOLRCORE = config.get('locviewer', 'SOLRCORE')
TITLE = config.get('locviewer', 'TITLE')
# SUGGESTIONS = config.get('locviewer', 'SUGGESTIONS')
#LAYOUT = config.get('locviewer', 'LAYOUT')

import sys, json, re
import cgi
import cgitb;

cgitb.enable()  # for troubleshooting
import psycopg2

form = cgi.FieldStorage()

timeoutcommand = 'set statement_timeout to 500'


def getlocations(connect_string):
    postgresdb = psycopg2.connect(connect_string)
    cursor = postgresdb.cursor()

    try:
        #sys.stderr.write('template %s' % template)

        #query = """select lc.id,refname,regexp_replace(refname, '^.*\\)''(.*)''$', '\\1') AS location, count(*) from locations_common lc
        #join movements_common mc on mc.currentlocation = lc.refname group by lc.id,refname"""

        query = """select regexp_replace(cc.computedcurrentlocation, '^.*\\)''(.*)''$', '\\1') AS location,
                   regexp_replace(cb.computedcrate, '^.*\\)''(.*)''$', '\\1') AS crate,
                   cc.computedcurrentlocation, cb.computedcrate,
                   count(*)
                   from collectionobjects_common cc
                   join collectionobjects_anthropology cb on (cb.id=cc.id)
                   group by cc.computedcurrentlocation, cb.computedcrate"""

        cursor.execute(query)
        result = {}
        for location,crate,locRefname,crateRefname,count in cursor.fetchall():

            if location is None:
                continue

            if crate is None: crate = ''
            #print location,crate,locRefname,crateRefname,count
            locationParts = location.split(',', 1)
            mainlocation = locationParts[0]
            minorlocation = ' (here)' if len(locationParts) < 2 else locationParts[1]
            if not mainlocation in result:
                result[mainlocation] = []
            result[mainlocation].append([minorlocation, crate, count])

        lockeys = sorted(result)
        keys = [[key, sorted(result[key], key=itemgetter(0)), len(result[key])] for key in lockeys]
        return keys
        #return json.dumps(result)    # or "json.dump(result, sys.stdout)"

    except psycopg2.DatabaseError, e:
        sys.stderr.write('autosuggest select error: %s' % e)
        return None
    except:
        raise
        sys.stderr.write("some other autosuggest database error!")
        return None


@login_required()
def locations(request):
    if request.method == 'GET' and request.GET != {}:
        context = {'searchValues': request.GET}

        context = setConstants(context)

        #context['currentlocation_s'] = '*'
        #context['pgNum'] = pgNum if 'pgNum' in context else '1'
        #context['url'] = url
        #context['displayType'] = 'list'
        #context['pixonly'] = 'true'
        #context['title'] = TITLE

        # do search
        loginfo('start search', context, request)
        #context = doSearch(context)

        locations = getlocations(connect_string)
        context['locations'] = locations
        context['loginBtnNext'] = 'locviewer/'

        return render(request, 'viewLocations.html', context)

    else:
        return render(request, 'viewLocations.html',
                      {'title': TITLE, 'pgNum': 10, 'maxresults': 20,
                       'imageserver': IMAGESERVER, 'loginBtnNext': 'locviewer/'})
