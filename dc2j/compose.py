'''Gathers final data and composes an email'''

from model import *
from google.appengine.api import mail
from google.appengine.ext.webapp import template

import os

class Compose(webapp.RequestHandler):
    def compose(p, j, n, extras):
        template_values = {'p': p, 'j': j, 'n': n, 'extras': extras}
        htmlpath = os.path.join(os.path.dirname(__file__), 'email.html')
        html = template.render(htmlpath, template_values)
        subject = "FIXME"
        return subject, html

    def mail(j, subject, html):
        message = mail.EmailMessage(sender="FIXME <f@ix.me>", 
                                    subject=subject)
        message.to = j.email
        message.body = "FIXME"
        message.html = html
        message.send()

    def dbfetch(dcid):
        _p = Proposal.all().filter('dcid =', dcid).fetch(1)
        if len(_p)==0:
            self.error(404)
            return
        p = _p[0]
        jn_list = []
        for n_key in p.newspapers:
            n = Newspapers.get(n_key)
            for j_key in n.journalists:
                j = Journalists.get(j_key)
                if j.threshold != 0: #obvs could be expanded...
                    jn_list.append((j,n))
        return jn_list

    def post(self):
        dcid = self.request.get('dcid')
        p, jn_list, = dbfetch(dcid)
        extras = getextras(p)
        for (j,n) in jn_list:
            subject, html = compose(p, j, n, extras)
            mail(j, subject, html)


def main():
    application = webapp.WSGIApplication(
            [('/compose/go', Compose)],
                            debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
