'''Gathers final data and composes an email'''

from model import *
from google.appengine.api import mail
from google.appengine.ext.webapp import template

class Compose(webapp.RequestHandler):
    def post(self):
        return

def main():
    application = webapp.WSGIApplication(
            [('/compose/go', Compose)],
                            debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
