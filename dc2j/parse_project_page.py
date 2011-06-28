from BeautifulSoup import BeautifulSoup,NavigableString
import re

states = {'ALABAMA': 'AL', 'ALASKA': 'AK', 'AMERICAN SAMOA': 'AS', 'ARIZONA': 'AZ', 'ARKANSAS': 'AR', 'CALIFORNIA': 'CA', 'COLORADO': 'CO', 'CONNECTICUT': 'CT', 'DELAWARE': 'DE', 'DISTRICT OF COLUMBIA': 'DC', 'FEDERATED STATES OF MICRONESIA': 'FM', 'FLORIDA': 'FL', 'GEORGIA': 'GA', 'GUAM': 'GU', 'HAWAII': 'HI', 'IDAHO': 'ID', 'ILLINOIS': 'IL', 'INDIANA': 'IN', 'IOWA': 'IA', 'KANSAS': 'KS', 'KENTUCKY': 'KY', 'LOUISIANA': 'LA', 'MAINE': 'ME', 'MARSHALL ISLANDS': 'MH', 'MARYLAND': 'MD', 'MASSACHUSETTS': 'MA', 'MICHIGAN': 'MI', 'MINNESOTA': 'MN', 'MISSISSIPPI': 'MS', 'MISSOURI': 'MO', 'MONTANA': 'MT', 'NEBRASKA': 'NE', 'NEVADA': 'NV', 'NEW HAMPSHIRE': 'NH', 'NEW JERSEY': 'NJ', 'NEW MEXICO': 'NM', 'NEW YORK': 'NY', 'NORTH CAROLINA': 'NC', 'NORTH DAKOTA': 'ND', 'NORTHERN MARIANA ISLANDS': 'MP', 'OHIO': 'OH', 'OKLAHOMA': 'OK', 'OREGON': 'OR', 'PALAU': 'PW', 'PENNSYLVANIA': 'PA', 'PUERTO RICO': 'PR', 'RHODE ISLAND': 'RI', 'SOUTH CAROLINA': 'SC', 'SOUTH DAKOTA': 'SD', 'TENNESSEE': 'TN', 'TEXAS': 'TX', 'UTAH': 'UT', 'VERMONT': 'VT', 'VIRGIN ISLANDS': 'VI', 'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WEST VIRGINIA': 'WV', 'WISCONSIN': 'WI', 'WYOMING': 'WY'}


re_gradelevel = re.compile('Grade Level: (.*)Joined')
re_teacherjoin = re.compile('Joined: ([^<]+)')
re_teacherid = re.compile('/we-teach/([0-9]+)')
re_dollas = re.compile('\$([^ ]+)')
re_nonprint = re.compile('[\\t\\r\\n\"]')
re_statenames = re.compile('('+'|'.join(states.keys())+')', re.I)
re_stateabbrevs = re.compile(', (' + '|'.join(states.values())+')', re.I)
re_onlyabbrev = re.compile('|'.join(states.values()), re.I)

maketext = lambda x: re_nonprint.sub('',' '.join([y for y in x if isinstance(y,NavigableString)]))

def parse_proj_page(fetcher, url):
    """
    parses the page at the given url and returns a dict with the
    following:
    
    project_id
    my_students
    my_project
    my_students_need
    list of comments:
    - name
    - is_teacher (bool)
    - city
    - state
    - comment
    - apple    = # projects funded
    - horn     = # people recruited
    - school   = # schools where they supported > 3 teachers
    - monthly  = makes monthly payments (bool)
    
    TODO:
    - Get actual dates on comments instead of "4 days ago"
    - Order comments by date posted
    - Clean the text, perhaps. I haven't done that at all.
    """
    project = {}
    
    page = BeautifulSoup(fetcher(url))
    project['short_essay'] = page.find('div',id='shortEssay').getText()
    project['long_essay'] = page.find('div',id='longEssay').getText()
    project['url'] = url
    
    posts = page.findAll('div', 'pm .*')
    comments = []
    for post in posts:
        comment = {}
        comment['name'] = post.find('span',attrs={'class':'author'}).getText()
        comment['anonymous'] = ('A donor' in comment['name'])
        comment['is_teacher'] = 'teacher' in post.attrs[0][1]
        if comment['is_teacher']:
            comment['name'] = re.sub('the Teacher','',comment['name'])
        if re.search(r"donorschoose\.org", comment['name'], re.IGNORECASE):
            continue
        comment['date'] = post.find('span',attrs={'class':'date'}).getText()
        c = post.find('div', 'content')
        if c == None:
            c = post.find('div', 'messageBody')
        comment['text'] = maketext(c.contents)
        comment['citystate'] = re.sub("^from", "", post.find('span',attrs={'class':'cityState'}).getText())
        
        comments.append(comment)
        
    project['comments'] = comments

    project['teacherid'] = re_teacherid.findall(page.find('a', attrs={'title': 'See this teacher\'s page'}).attrMap['href'])[0]
	
    
    return project

def add_teacher_data(fetcher, teacherURL, project):
    page = BeautifulSoup(fetcher(teacherURL + project['teacherid'] + '?historical=true'))  
    # classroom description
    about = page.findAll('h2')[0]
    assert ('class', 'leadIn') in about.parent.attrs
    project['aboutClassroom'] = about.text
    # grade level, teacher join date
    teacherInfo = page.findAll('div', attrs={'class': 'teacherDetails'})[0].text
    project['gradeLevel'] = re_gradelevel.findall(teacherInfo)[0]
    project['teacherJoinDate'] = re_teacherjoin.findall(teacherInfo)[0]
    # info on completed projects
    _numProjects = [tag for tag in page.findAll('strong') if tag.parent.name=='td']
    if len(_numProjects) == 0: #no completed projects
        project['teacherNumProjects'] = 0
        project['teacherRaisedOnDC'] = 0
        return
    # number of completed projects
    project['teacherNumProjects'] = _numProjects[1].text
    # total money raised to date
    monies = page.findAll('span', attrs={'class': 'given'})
    each_project = lambda tag: int(re_dollas.findall(tag.text)[0].replace(',',''))
    project['teacherRaisedOnDC'] = sum(map(each_project, monies))
    return

def add_district_data(fetcher, project):
    page = BeautifulSoup(fetcher(project['url']))
    h5s = page.findAll('h5')
    i = ["District:" in h for h in h5s].index(True)
    district = h5s[i].findNext('a')
    district_url = district.get('href')
    district_str = district.contents
    project['district'] = district_str[0]
    project['district_url'] = district_url
    page = BeautifulSoup(fetcher(project['district_url']))
    tds = page.findAll('td')
    i = [("Projects1-" in h.text) and (len(h.contents)==4) for h in tds].index(True)
    num_proj = int(tds[i].findChildren('strong')[1].text)
    project['num_proj_in_district'] = num_proj


def tabulate_states(comments):
    # stateful! modified each comment to include a state as well as building statecounts
    statecounts = {}
    # apologies to PEP-8
    for comment in comments:
        if comment['is_teacher']: continue
        fullname = re_statenames.findall(comment['citystate'])
        if len(fullname) > 0:
            abbrev = states[fullname[0].upper()]
            comment['state'] = abbrev
        else:
            abbrevstr = re_stateabbrevs.findall(comment['citystate'])
            if len(abbrevstr) > 0:
                abbrev = abbrevstr[0]
                comment['state'] = abbrev
            else:
                abbrevonly = re_onlyabbrev.findall(comment['citystate'])
                if len(abbrevonly) > 0:
                    abbrev = abbrevonly[0]
                    comment['state'] = abbrev
                else:
                    comment['state'] = None
                    continue
        statecounts[abbrev] = statecounts.get(abbrev,0) + 1
    return statecounts

def scrapeDC(fetcher, url, teacherURL):
    project = parse_proj_page(fetcher, url)
    add_teacher_data(fetcher, teacherURL, project)
    add_district_data(fetcher, project)
    project['statecounts'] = tabulate_states(project['comments'])
    return project


if __name__ == "__main__":
    from urllib2 import urlopen
    import json
    fetcher = lambda url: urlopen(url)
    #fetcher = lambda url: open(url)
    url="http://www.donorschoose.org/donors/proposal.html?id=569177"
    teacherURL = "http://www.donorschoose.org/we-teach/"

    #url="/home/mshron/Dropbox/Public/dc2j/proposal.html?id=504497"
    #teacherURL="/home/mshron/Dropbox/Public/dc2j/"
    p=scrapeDC(fetcher, url, teacherURL)
    print json.dumps(p)
