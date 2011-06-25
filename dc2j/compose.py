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

    def cardinal2word(self, n):
        if n <= 0:
            return "No"
        if n == 1:
            return "One"
        if n < 21:
            return ['Two','Three','Four','Five','Six','Seven','Eight','Nine','Ten','Eleven','Twelve','Thirteen','Fourteen','Fifteen','Sixteen','Seventeen','Eighteen','Nineteen','Twenty'][n-2]
        else:
            return str(n)

    def ordinal2word(self, n):
        if n <= 1:
            return 'first'
        if n < 21:
            return ['second','third','fourth','fifth','sixth','seventh','eighth','ninth','tenth','eleventh','twelfth','thirteenth','fourteenth','fifteenth','sixteenth','seventeenth','eighteenth','ninteenth','twentieth'][n-2] 
        else:
            if n%10 == 1:
                return '%sst'%n
            elif n%10 == 2:
                return '%snd'%n
            elif n%10 == 3:
                return '%srd'%n
            else:
                return '%sth'%n


    def addstatedata(self, extras, state):
        statecounts = extras['statecounts']
        instate = statecounts[state]
        outstate = sum(map(int,statecounts.values()))-instate
        extras['instate'] = instate > 0
        extras['outofstate'] = outstate > 0
        extras['numInstateDonorsText'] = self.cardinal2word(instate) + \
                                (' person' if instate==1 else ' people')
        extras['numOutstateDonorsText'] = self.cardinal2word(outstate) + \
                                (' person' if instate==1 else ' people')
        extras['teacherNumProjectsText'] =  self.ordinal2word(extras['teacherNumProjects']) + \
                                 ' completed project'

    def interesting(self, comment):
        if len(comment['text']) < 60:
            return False
        if len(comment['text']) > 300:
            return False
        return True

    def getextras(self, dcid, p):
        extras = scrapeDC(self.fetcher, DCpublicurl + dcid, teacherURL)            
        extras['donors'] = [c for c in extras['comments'] if (not c['is_teacher'] and self.interesting(c))]
        extras['donorcount'] = len(extras['donors'])
        self.addstatedata(extras, p.state)
        return extras

    def post(self):
        dcid = self.request.get('dcid')
        p, jn_list = self.dbfetch(dcid)
        extras = self.getextras(dcid, p)
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
