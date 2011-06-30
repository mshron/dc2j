'''Gathers final data and composes an email'''

from model import *
from google.appengine.api import mail
from google.appengine.ext.webapp import template
import logging
import os
import re

from parse_project_page import scrapeDC

class Compose(webapp.RequestHandler):
    def compose(self,p, j, n, extras):
        urlparams = {'jid': j.jid, 'dcid': p.dcid}
        url = 'http://dc2jpr.appspot.com/dc/project?' +\
                              urlencode(urlparams)
        template_values = {'p': p, 'j': j, 'n': n, 
                            'extras': extras,
                            'url': url}
        htmlpath = os.path.join(os.path.dirname(__file__), 'email.html')
        html = template.render(htmlpath, template_values)
        textpath = os.path.join(os.path.dirname(__file__), 'email.txt')
        plaintext = template.render(textpath, template_values)
        subject = "Micro-philanthropy at work at %s"%(p.schoolName)
        return subject, html, plaintext, url

    def mail(self, j, n, subject, html, plaintext, url):
        message = mail.EmailMessage(sender="DC2J <max.shron@gmail.com>", 
                                    subject=subject)
        message.to = "max.shron@gmail.com" #j.email
        message.body = plaintext
        message.html = html
        message.send()
        l = Letters()
        l.html = re.sub('&action=i','',html)
        l.html = re.sub('\?jid=[^"]+','/',html)
        l.journalist = j.fullName
        l.newspaper = n.name
        l.nurl = url
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
                if j.threshold != 0.0: #obvs could be expanded...
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
            return ['two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen','twenty'][n-2]
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
        extras['ins'] = instate
        outstate = sum(map(int,statecounts.values()))-instate
        extras['outs'] = outstate
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

    def trim(self, _donors, p):
        locale_flag = False
        quality = []
        for comment in _donors:
            q = comment['text'].count('.')
            if comment['citystate']:
                q += 1
            if comment['state']:
                q += 1
            if comment['state'] == p.state:
                if locale_flag is False:
                    q += 1
                    locale_flag = True
                    logging.info('commenting diversity satisfied!')
            if "strong believer" in comment['text']:
                q = 0
            quality.append(q)
        idx = sorted(range(len(quality)), key=quality.__getitem__, reverse=True)
        return [_donors[i] for i in idx][:2]

    def getextras(self, dcid, p):
        extras = scrapeDC(self.fetcher, DCpublicurl + dcid, teacherURL)            
        _donors = [c for c in extras['comments'] if (not c['is_teacher'] and self.interesting(c))]
        self.addstatedata(extras, p.state)
        extras['donors'] = self.trim(_donors, p)
        extras['donorcount'] = len(extras['donors'])
        extras['numProjectsDistrictText'] = self.ordinal2word(extras['num_proj_in_district'])
        extras['numdonors'] = extras['ins']-extras['outs']
        extras['numdonorsText'] = self.cardinal2word(extras['numdonors']).capitalize()
        extras['numdonors-2'] = extras['numdonors']-2
        extras['numdonors-2Text'] = self.cardinal2word(extras['numdonors-2'])
        return extras

    def post(self):
        dcid = self.request.get('dcid')
        p, jn_list = self.dbfetch(dcid)
        extras = self.getextras(dcid, p)
        for (j,n) in jn_list:
            subject, html, plaintext, url = self.compose(p, j, n, extras)
            self.mail(j, n, subject, html, plaintext, url)
            j.actions.append('S:%s'%dcid)
            j.put()


def main():
    application = webapp.WSGIApplication(
            [('/compose/go', Compose)],
                            debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
