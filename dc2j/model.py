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

DCpublicurl = "http://www.donorschoose.org/donors/proposal.html?id="

class Newspaper(db.Model):
    url = db.LinkProperty(required=True)
    nid = db.StringProperty(required=True)
    journalists = db.ListProperty(db.Key)
    centerLatLng = db.GeoPtProperty()
    nwLatLng = db.GeoPtProperty()
    seLatLng = db.GeoPtProperty()
    name = db.StringProperty()

class Journalist(db.Model):
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
    html = db.Text()
    journalist = db.String()
    newspaper = db.String()
    time = db.DateTimeProperty(auto_now=True)
    nurl = db.LinkProperty()
