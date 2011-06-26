from model import *
import os
from google.appengine.ext.webapp import template

class Index(webapp.RequestHandler):
    def get(self):
        l = Letters.all().order('-time') 
        htmlpath = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(htmlpath, {'l': l}))

def main():
    application = webapp.WSGIApplication([('/', Index)],
                                         debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":  
    main()
