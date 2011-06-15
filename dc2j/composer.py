'''Scrapes/picks/composes dc projects into emails'''
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.taskqueue import Task
from google.appengine.api.urlfetch import fetch
from google.appengine.ext import db

from django.utils import simplejson as json

from urllib import urlencode
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
    newspaper = db.ReferenceProperty(reference_class=Newspaper)
    email = db.EmailProperty(required=True)
    threshold = db.FloatProperty()
    hasName = db.BooleanProperty(required=True)
    fullName = db.StringProperty()

class Proposal(db.Expando):
    title = db.StringProperty(required=True)
    dcid = db.StringProperty(required=True)
    url = db.LinkProperty(required=True)
    status = db.StringProperty()
    teacher = db.StringProperty()
    fulfillmentTrailer = db.StringProperty()
    schoolLatLng = db.GeoPtProperty()
    money = db.IntegerProperty()
    city = db.StringProperty()
    state = db.StringProperty()
    newspapers = db.ListProperty(db.Key)
    time = db.DateTimeProperty(auto_now=True)


# called by spreadsheet reader to insert DC data into the db
class SimplePollDC(webapp.RequestHandler):
    def requestURL(self, n):
        params = {'nwLat': n.nwLatLng.lat,
                  'nwLng': n.nwLatLng.lon,
                  'seLat': n.seLatLng.lat,
                  'seLng': n.seLatLng.lon,
                  'max': 50}
        url = DCapi + urlencode(params)
        return url
        
    def fetch(self, url):
        body = fetch(url).content
        data = json.loads(body)
        return data

    # status is always updated, no matter whether it is changed or not;
    # thus, the timestamp is always up to date
    def update(self, _p, pro, n): #TODO these two are untested
        p = _p[0]
        status = pro['fundingStatus']
        p.status = status
        k = n.key()
        if k not in p.newspapers:
            p.newspapers.append(k)
        p.put()

    def insert(self, pro, n):
        p = Proposal(dcid = pro['id'],
                     title = pro['title'],
                     url = pro['proposalURL'],
                     status = pro['fundingStatus'])
        p.newspapers.append(n.key())
        p.put()
        
    def post(self):
        newspaper = self.request.get('nid')
        _n = Newspaper.all().filter('nid =', newspaper).fetch(1)
        if len(_n)==0:
            self.error(404)
            return
        n = _n[0]
        url = self.requestURL(n)
        data = self.fetch(url)
        if len(data)==0:
            self.error(412)
        # TODO check for >50 replies; should we chuck it, too noisy?
        for proposal in data['proposals']:
            dcid = proposal['id']
            _p = Proposal.all().filter('dcid =', dcid).fetch(1)
            if len(_p) == 0: self.insert(proposal, n)
            else: self.update(_p[0], proposal, n)

#called by cron job that finds week-long unmodified proposals
class QueryProjectDC(webapp.RequestHandler): 
    def queryURL(self, p):
        params = {'historical': True,
                  'solrQuery': 'id:%s'%p.dcid}
        url = DCapi + urlencode(params)
        return url

    def fetch(self, url): #D.R.Y....
        body = fetch(url).content
        data = json.loads(body)
        return data

    def augment(self, p, pro):
        p.teacher = pro['teacherName'],
        p.fulfillmentTrailer = pro['fulfillmentTrailer'],
        p.schoolLatLat = db.GeoPt(pro['latitude'], pro['longitude']),
        p.money = pro['totalPrice'],
        p.city = pro['city'],
        p.state = pro['state']
        p.put()

    def post(self):
        dcid = self.request.get('dcid')
        _p = Proposal.all().filter('dcid =', dcid).fetch(1)
        if len(_p) == 0:
            self.error(404)
            return
        p = _p[0]
        url = self.queryURL(p)
        proposal = self.fetch(url)
        if proposal['totalProposals'] != 1: #in inbetween stage #TODO
            self.error(412)
            return
        else:
            augment(p, proposal)
            # this could use a key to save a db call,
            # at the expense of API sloppiness
            t = Task(url="/alert", params={'dcid': dcid})
            
class SendAlerts(webapp.RequestHandler):
    def post(self):
        dcid = self.request.get('dcid')
        _p = Proposal.all().filter('dcid =', dcid).fetch(1)
        if len(_p)==0:
            self.error(404)
            return
        p = _p[0]

    
class Newspapers(webapp.RequestHandler):
    def put(self):
        rows = csv.reader(self.request.body_file)
        for i,row in enumerate(rows):
            if i == 0:
                titles = row
                continue
            if len(row) == 0: continue
            data = dict(zip(titles, row))
            nid = data['nid']
            _n = Newspaper.all().filter('nid =', nid).fetch(1)
            if _n: n = _n[0]
            else: n = Newspaper(nid = nid, url = data['url'])
            n.nid = nid
            n.url = data['url']
            lat = float(data['lat'])
            lng = float(data['lng'])
            n.centerLatLng = db.GeoPt(lat,lng)
            offsetLat = float(data['offsetLat'])
            offsetLng = float(data['offsetLng'])
            n.nwLatLng = db.GeoPt(lat+offsetLat, 
                                  lng-offsetLng)
            n.seLatLng = db.GeoPt(lat-offsetLat,
                                  lng+offsetLng)
            n.name = data.get('name')
            n.put()

    def get(self): #doesn't do much at the moment
        nid = self.request.get('nid')
        if not nid:
          n = Newspaper.all().fetch(10)
          self.response.out.write(str(n))
          return
        n = Newspaper.all().filter('nid =', nid).fetch(10)
        self.response.out.write(str(n))

def main():
    application = webapp.WSGIApplication([('/newspapers', Newspapers),
                                          ('/simplepolldc', SimplePollDC),
                                          ('/querydc',QueryProjectDC)],
                            debug=True)
    run_wsgi_app(application)
            
if __name__ == "__main__":
    main()
