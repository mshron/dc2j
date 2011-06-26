'''Interactive friendsourcing tool'''

from model import *
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
            n = _n[0]
        if n == None:
            self.error(412) #FIXME
        htmlpath = os.path.join(os.path.dirname(__file__), 'addjournalist.html')
        self.response.out.write(template.render(htmlpath, {'n': n, 'range': range(3)}))

    def put(self):
       return 
        
        

def main():
    application = webapp.WSGIApplication(
        [('/input/journalists', AddJournalists)],
            debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
