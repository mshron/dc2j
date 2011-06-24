from BeautifulSoup import BeautifulSoup,NavigableString
import re

re_gradelevel = re.compile('Grade Level: (.*)Joined')
re_teacherjoin = re.compile('Joined: ([^<]+)')
re_teacherid = re.compile('/we-teach/([0-9]+)')
re_dollas = re.compile('\$([^ ]+)')
re_nonprint = re.compile('[\\t\\r\\n\"]')

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
    
    teacher_posts = page.findAll('div', attrs={'class':'pm  teacher'})
    donor_posts = page.findAll('div', attrs={'class':'pm  '})
    comments = []
    for post in teacher_posts:
        comment = {}
        comment['date'] = post.find('span',attrs={'class':'date'}).getText()
        comment['is_teacher'] = True
        comment['name'] = re.sub("the Teacher", "", post.find('span',attrs={'class':'author'}).getText())
        c = post.find('div', 'content')
        if c == None:
            c = post.find('div', 'messageBody')
        comment['text'] = maketext(c.contents)
        comment['citystate'] = re.sub("^from", "", post.find('span',attrs={'class':'cityState'}).getText())
        comment['anonymous'] = False
        comments.append(comment)
    
    for post in donor_posts:
        comment = {}
        comment['name'] = post.find('span',attrs={'class':'author'}).getText()
        comment['anonymous'] = (comment['name'] == 'A donor')
        if re.search(r"donorschoose\.org", comment['name'], re.IGNORECASE):
            continue
        comment['date'] = post.find('span',attrs={'class':'date'}).getText()
        comment['is_teacher'] = False
        comment['text'] = maketext(post.find("div",attrs={'class':'content '}).contents)
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

def scrapeDC(fetcher, url, teacherURL):
    project = parse_proj_page(fetcher, url)
    add_teacher_data(fetcher, teacherURL, project)
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
