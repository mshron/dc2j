'''Scrapes/maintains dc projects into database. Calls composer when needed.'''

from model import *
from random import random

class Newspapers(webapp.RequestHandler):
    def put(self):
        rows = csv.reader(self.request.body_file, delimiter='|')
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
            n.name = data['name']
            n.city = data['city']
            n.state = data['state']
            n.error = data['error']
            n.rndm = random()
            n.put()

    def post(self):
        nid = self.request.get('nid')
        _n = Newspaper.all().filter('nid =', nid).fetch(1)
        if _n == None:
            self.error(404)
            return
        n = _n[0]
        lat = float(self.request.get('lat'))
        lng = float(self.request.get('lng'))
        n.centerLatLng = db.GeoPt(lat,lng)
        offsetLat = float(self.request.get('offsetLat'))
        offsetLng = float(self.request.get('offsetLng'))
        n.nwLatLng = db.GeoPt(lat+offsetLat, 
                              lng-offsetLng)
        n.seLatLng = db.GeoPt(lat-offsetLat,
                              lng+offsetLng)
        n.put()
        params = {'nid': nid}
        t = Task(url='/data/task/polldc', params=params)
        t.add()

    def get(self): #doesn't do much at the moment
        nid = self.request.get('nid')
        if not nid:
          n = Newspaper.all().fetch(10)
          self.response.out.write(str(n))
          return
        n = Newspaper.all().filter('nid =', nid).fetch(10)
        self.response.out.write(str(n))

class Journalists(webapp.RequestHandler):
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
            else:
                msg = "Line %i - newspaper %s not found\n"%(i, nid)
                self.response.out.write(msg)
                continue
            # be careful -- not idempotent!
            jid = hex(randint(0,2**32))[2:] 
            j = Journalist(jid = jid)
            j.email = data['email']
            j.threshold = .5
            j.isPerson = data['isPerson'].lower() in \
                         ['y', 'yes', 't', 'true'] 
            j.fullName = data['name']
            j.put()
            n.journalists.append(j.key())
            n.put()


# called to insert DC data into the db
class PollDC(webapp.RequestHandler):
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
                     status = pro['fundingStatus'],
                     accessfails = 0)
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
            else: self.update(_p, proposal, n)

class FindUnmodifiedCron(webapp.RequestHandler):
    def get(self):
        now = datetime.now()
        then = now - timedelta(60*24*7) # 1 week ago
        query = Proposal.all()
        query.filter("time <=", now)
        query.filter("accessfails <=", 10) # up to 10 retries
        for proposal in query:
            params = {'dcid': proposal.dcid}
            t = Task(url='/data/task/querydc', params=params)
            t.add()

#called by cron job that finds week-long unmodified proposals
class QueryProjectDC(webapp.RequestHandler): 
    def queryURL(self, p):
# params = {'historical': True, #FIXME
#                  'solrQuery': 'id:%s'%p.dcid}
        params = {'id': p.dcid}
        url = DCapi + urlencode(params)
        return url

    def fetch(self, url): #D.R.Y....
        body = fetch(url).content
        data = json.loads(body)
        return data

    def augment(self, p, _pro):
        pro = _pro['proposals'][0]
        p.teacher = pro['teacherName']
        p.fulfillmentTrailer = pro['fulfillmentTrailer']
        #p.shortDescription = pro['shortDescription']
        p.schoolName = pro['schoolName']
        p.schoolLatLat = db.GeoPt(pro['latitude'], pro['longitude'])
        p.money = pro['totalPrice']
        p.city = pro['city']
        p.state = pro['state']
        p.resource = pro['resource']['name']
        p.subject = pro['subject']['name']
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
        if proposal['totalProposals'] != '1': #inbetween stage or deleted
            p.accessfails += 1
            p.put()
            self.error(412)
            return
        else:
            self.augment(p, proposal)
            # this could use a key to save a db call,
            # at the expense of API sloppiness
            t = Task(url="/compose/go", params={'dcid': dcid})
            t.add()
            
def main():
    application = webapp.WSGIApplication(
            [('/data/newspapers', Newspapers),
            ('/data/journalists', Journalists),
            ('/data/task/polldc', PollDC),
            ('/data/task/querydc', QueryProjectDC),
            ('/data/cron/unmodified', FindUnmodifiedCron)],
                            debug=True)
    run_wsgi_app(application)
            
if __name__ == "__main__":
    main()
