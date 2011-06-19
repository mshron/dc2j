'''Gathers final data and composes an email'''

from model import *
from google.appengine.api import mail
from google.appengine.ext.webapp import template

class Compose(webapp.RequestHandler):
    def post(self):
        dcid = self.request.get('dcid')
        _p = Proposal.all().filter('dcid =', dcid).fetch(1)
        if len(_p)==0:
            self.error(404)
            return
        p = _p[0]


        return

def main():
    application = webapp.WSGIApplication(
            [('/compose/go', Compose)],
                            debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
