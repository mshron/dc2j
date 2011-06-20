from BeautifulSoup import BeautifulSoup
import re

re_gradelevel = re.compile('Grade Level: ([0-9]+)')
re_teacherjoin = re.compile('Joined: ([^<]+)')
re_dollas = re.compile('\$([^ ]+)')

def parse_proj_page(url):
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
    
    page = BeautifulSoup(fetch(url).content)
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
        comment['comment'] = re.sub(r'"', '', post.find("div",attrs={'class':'content '}).getText())
        comment['citystate'] = re.sub("^from", "", post.find('span',attrs={'class':'cityState'}).getText())
        comments.append(comment)
    
    for post in donor_posts:
        comment = {}
        comment['name'] = post.find('span',attrs={'class':'author'}).getText()
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

def add_teacher_data(project):
    page = BeautifulSoup(fetch(project['teacherURL'] + '?historical=True').content)  
    # classroom description
    about = page.find('h2')[0]
    assert ('class', 'leadIn') in about.parent.attrs
    project['aboutClassroom'] = about.text
    # grade level, teacher join date
    teacherInfo = page.findAll('div', attrs={'class': 'teacherDetails'})[0].text
    project['gradeLevel'] = re_gradelevel(teacherInfo)
    project['teacherJoinDate'] = re_teacherjoin(teacherInfo)
    # info on completed projects
    _numProjects = [tag for tag in page.findAll('strong') if tag.parent.name=='td']
    if len(_numProjects) == 0: #no completed projects
        project['teacherNumProjects'] = 0
        project['teacherRaisedOnDC'] = 0
        return
    # number of completed projects
    project['teacherNumProjects'] = _numProject[1].text
    # total money raised to date
    monies = page.findAll('span', attrs={'class': 'given'})
    each_project = lambda tag: int(re_dollas.findall(tag.text)[0].replace(',',''))
    project['teacherRaisedOnDC'] = sum(map(each_project, monies))
    return

def scrapeDC(url):
    project = parse_proj_page(url)
    add_teacher_data(project)

    extras = {}
    


if __name__ == "__main__":
    url="http://www.donorschoose.org/donors/proposal.html?id=569177"
    p=parse_proj_page(url)
    print json.dumps(p)
