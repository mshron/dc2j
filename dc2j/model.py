from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.taskqueue import Task
from google.appengine.api.urlfetch import fetch
from google.appengine.ext import db

from django.utils import simplejson as json

from urllib import urlencode
from datetime import datetime, timedelta
from random import randint
import csv

## hardcoded constants
DCapi = "http://api.donorschoose.org/common/json_feed.html?APIKey=73zfti7me2in&"

class Newspaper(db.Model):
    url = db.LinkProperty(required=True)
    nid = db.StringProperty(required=True)
    centerLatLng = db.GeoPtProperty()
    nwLatLng = db.GeoPtProperty()
    seLatLng = db.GeoPtProperty()
    name = db.StringProperty()

class Journalist(db.Model):
    newspaper = db.ReferenceProperty(reference_class=Newspaper, 
                                    required=True)
    jid = db.StringProperty(required=True)
    email = db.EmailProperty()
    threshold = db.FloatProperty()
    isPerson = db.BooleanProperty()
    fullName = db.StringProperty()

class Proposal(db.Expando):
    title = db.StringProperty(required=True)
    dcid = db.StringProperty(required=True)
    url = db.LinkProperty(required=True)
    accessfails = db.IntegerProperty()
    status = db.StringProperty()
    time = db.DateTimeProperty(auto_now=True)

## expando...
#    teacher = db.StringProperty()
#    fulfillmentTrailer = db.StringProperty()
#    shortDescription = db.StringProperty()
#    schoolLatLng = db.GeoPtProperty()
#    money = db.IntegerProperty()
#    city = db.StringProperty()
#    state = db.StringProperty()
#    newspapers = db.ListProperty(db.Key)
#    subject = db.StringProperty()
#    resource = db.StringProperty()


