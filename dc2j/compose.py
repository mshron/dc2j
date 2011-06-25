'''Gathers final data and composes an email'''

from model import *
from google.appengine.api import mail
from google.appengine.ext.webapp import template

import os

from parse_project_page import scrapeDC

class Compose(webapp.RequestHandler):
    def compose(self,p, j, n, extras):
        template_values = {'p': p, 'j': j, 'n': n, 'extras': extras}
        htmlpath = os.path.join(os.path.dirname(__file__), 'email.html')
        html = template.render(htmlpath, template_values)
        subject = "FIXME"
        return subject, html

    def mail(self, j, n, subject, html):
        message = mail.EmailMessage(sender="FIXME <max.shron@gmail.com>", 
                                    subject=subject)
        message.to = j.email
        message.body = "FIXME"
        message.html = html
        message.send()
        l = Letters()
        l.html = html
        l.journalist = j.fullName
        l.newspaper = n.name
        l.nurl = n.url
        l.put()


    def dbfetch(self,dcid):
        _p = Proposal.all().filter('dcid =', dcid).fetch(1)
        if len(_p)==0:
            self.error(404)
            return
        p = _p[0]
        jn_list = []
        for n_key in p.newspapers:
            n = Newspaper.get(n_key)
            for j_key in n.journalists:
                j = Journalist.get(j_key)
                if j.threshold != 0: #obvs could be expanded...
                    jn_list.append((j,n))
        return p, jn_list

    def fetcher(self, url):
        return fetch(url).content

    def getextras(self,dcid):
        extras = scrapeDC(self.fetcher, DCpublicurl + dcid, teacherURL)            
        extras['donors'] = [c for c in extras['comments'] if not c['is_teacher']]
        return extras

    def post(self):
        dcid = self.request.get('dcid')
        p, jn_list = self.dbfetch(dcid)
        extras = self.getextras(dcid)
        for (j,n) in jn_list:
            subject, html = self.compose(p, j, n, extras)
            self.mail(j, n, subject, html)


def main():
    application = webapp.WSGIApplication(
            [('/compose/go', Compose)],
                            debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
