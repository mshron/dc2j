from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.taskqueue import Task
from google.appengine.api.urlfetch import fetch
from google.appengine.ext import db

from django.utils import simplejson as json

from urllib import urlencode
from urllib2 import urlopen
from datetime import datetime, timedelta
from random import randint
import logging
import csv

## hardcoded constants
#DCapi = "http://api.donorschoose.org/common/json_feed.html?APIKey=73zfti7me2in&"
DCapi = "http://dl.dropbox.com/u/7481916/dc2j/"
DCpublicurl = "http://www.donorschoose.org/donors/proposal.html?id="
teacherURL = "http://www.donorschoose.org/we-teach/"

#testing
#DCapi = "http://localhost/"
#DCpublicurl = "http://localhost/"
#teacherURL = "http://localhost/"

class Newspaper(db.Model):
    url = db.LinkProperty(required=True)
    nid = db.StringProperty(required=True)
    journalists = db.ListProperty(db.Key)
    centerLatLng = db.GeoPtProperty()
    nwLatLng = db.GeoPtProperty()
    seLatLng = db.GeoPtProperty()
    name = db.StringProperty()
    city = db.StringProperty()
    state = db.StringProperty()
    error = db.StringProperty()
    rndm = db.FloatProperty()

class Journalist(db.Model):
    jid = db.StringProperty(required=True)
    email = db.EmailProperty()
    threshold = db.FloatProperty()
    isPerson = db.BooleanProperty()
    fullName = db.StringProperty()
    actions = db.ListProperty(str)


class Proposal(db.Expando):
    title = db.StringProperty(required=True)
    dcid = db.StringProperty(required=True)
    accessfails = db.IntegerProperty()
    status = db.StringProperty()
    time = db.DateTimeProperty(auto_now=True)
    newspapers = db.ListProperty(db.Key)

## expando...
#    teacher = db.StringProperty()
#    fulfillmentTrailer = db.StringProperty()
#    shortDescription = db.StringProperty()
#    schoolLatLng = db.GeoPtProperty()
#    money = db.IntegerProperty()
#    city = db.StringProperty()
#    state = db.StringProperty()
#    subject = db.StringProperty()
#    resource = db.StringProperty()

class Letters(db.Model):
    html = db.TextProperty()
    journalist = db.StringProperty()
    newspaper = db.StringProperty()
    time = db.DateTimeProperty(auto_now=True)
    nurl = db.LinkProperty()
