'''Provides pixel and url forwarding for the emails'''

from model import *

class ProjectURL(webapp.RequestHandler):
    def get(self):
        dcid = self.request.get('dcid')
        jid = self.request.get('jid') 
        action = self.request.get('action')
        j = Journalist.all().filter('jid =',jid).get()
        if action == 'u':
            j.actions.append('U:%s'%dcid)
            self.redirect(DCpublicurl + dcid)  
        if action == 'i':
            j.actions.append('I:%s'%dcid)  
            self.redirect('/static/pixel.png')
        else:
            self.redirect('/static/pixel.png')

        j.put()

def main():
    application = webapp.WSGIApplication(
                [('/dc/project', ProjectURL)],
                debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
        
        
        
