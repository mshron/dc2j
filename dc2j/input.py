'''Interactive friendsourcing tool'''

from model import *
import logging
import os
from random import random
from google.appengine.ext.webapp import template


class AddJournalists(webapp.RequestHandler):
    def get(self):
        n = None
        count = 0
        while n == None and count < 50:
            r = random()
            _n = Newspaper.all().filter('rndm >=', r).fetch(1)
            if _n == None:
                count += 1
                continue
            if len(_n[0].journalists) > 0:
                continue
            if (_n[0].error != ""):
                continue
            n = _n[0]
        if n == None:
            self.error(412) #FIXME
        htmlpath = os.path.join(os.path.dirname(__file__), 'addjournalist.html')
        self.response.out.write(template.render(htmlpath, {'n': n, 'range': range(3)}))

    def post(self):
        nid = self.request.get('nid')
        _n = Newspaper.all().filter('nid =', nid).fetch(1)
        if _n: n = _n[0]
        else:
            logging.error("%s was created then not found!"%nid)
            self.redirect('/input/jounralists')
        error = self.request.get('error')
        if error != None:
            n.error = error
            n.put()
            self.redirect('/input/journalists') 
        for r in xrange(3):
            email = self.request.get('email-%s'%r)
            name = self.request.get('name-%s'%r)
            isperson = self.request.get('isperson-%s'%r)
            if email != "":
                jid = hex(randint(0,2**32))[2:] 
                j = Journalist(jid = jid)
                j.email = email 
                j.threshold = .5
                j.isPerson = isperson=='on'
                j.fullName = name
                j.put()
                n.journalists.append(j.key())
                n.put()

        self.redirect('/input/journalists')

class Unsubscribe(webapp.RequestHandler):
    def get(self):
        jid = self.request.get('jid')
        j = Journalist.all().filter('jid =',jid).get()
        if j == None:
            self.error(404)
            return
        j.threshold = 0.0
        j.actions.append('KIA')
        j.put()
        self.redirect('/static/noemail.html')
        
def main():
    application = webapp.WSGIApplication(
        [('/input/journalists', AddJournalists),
         ('/input/unsubscribe', Unsubscribe)],
            debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
