from BeautifulSoup import BeautifulSoup
import re

re_gradelevel = re.compile('Grade Level: (.*)Joined')
re_teacherjoin = re.compile('Joined: ([^<]+)')
re_dollas = re.compile('\$([^ ]+)')

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
    # teacher posts are commented out for the moment because I don't know how to deal with letters in place of comments
#    for post in teacher_posts:
#        comment = {}
#        comment['date'] = post.find('span',attrs={'class':'date'}).getText()
#        comment['is_teacher'] = True
#        comment['name'] = re.sub("the Teacher", "", post.find('span',attrs={'class':'author'}).getText())
#        comment['comment'] = re.sub(r'"', '', post.find("div",['content', 'letter']).getText())
#        comment['citystate'] = re.sub("^from", "", post.find('span',attrs={'class':'cityState'}).getText())
#        comment['anonymous'] = False
#        comments.append(comment)
    
    for post in donor_posts:
        comment = {}
        comment['name'] = post.find('span',attrs={'class':'author'}).getText()
        comment['anonymous'] = (comment['name'] == 'A donor')
        if re.search(r"donorschoose\.org", comment['name'], re.IGNORECASE):
            continue
        comment['date'] = post.find('span',attrs={'class':'date'}).getText()
        comment['is_teacher'] = False
        comment['comment'] = re.sub(r'"', '', post.find("div",attrs={'class':'content '}).getText())
        comment['citystate'] = re.sub("^from", "", post.find('span',attrs={'class':'cityState'}).getText())
        
        comments.append(comment)
        
    project['comments'] = comments

    project['teacherURL'] = page.find('a', attrs={'title': 'See this teacher\'s page'}).attrMap['href']
    
    return project

def add_teacher_data(fetcher, project):
    page = BeautifulSoup(fetcher(project['teacherURL'] + '?historical=True'))  
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

def scrapeDC(fetcher, url):
    project = parse_proj_page(fetcher, url)
    add_teacher_data(fetcher, project)
    return project
    


if __name__ == "__main__":
    from urllib2 import urlopen
    import json
    fetcher = lambda url: urlopen(url)
    url="http://www.donorschoose.org/donors/proposal.html?id=569177"
    p=scrapeDC(fetcher, url)
    print json.dumps(p)