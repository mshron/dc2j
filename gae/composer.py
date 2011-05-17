'''Scrapes/picks/composes dc projects into emails'''
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.ext import db

class Newspaper(db.Model):
    url = db.LinkProperty(required=True)
    uid = db.StringProperty(required=True)
    nwLatLng = db.GeoPtProperty()
    seLatLng = db.GeoPtProperty()
    longName = db.StringProperty()

class Journalist(db.Model):
    newspaper = db.ReferenceProperty(reference_class=Newspaper)
    email = db.EmailProperty(required=True)
    threshold = db.FloatProperty()
    hasName = db.BooleanProperty(required=True)
    fullName = db.StringProperty()

class Proposal(db.Expando):
    title = db.StringProperty(required=True)
    dcid = db.StringProperty(required=True)
    url = db.LinkProperty(required=True)
    shortDescription = db.StringProperty()
    schoolLatLng = db.GeoPtProperty()
    money = db.IntegerProperty()
    newspapers = db.ListProperty(db.ReferenceProperty(reference_class=Newspaper))
    
class Newspapers(webapp.RequestHandler):
    def post(self):
        

