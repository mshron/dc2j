from BeautifulSoup import BeautifulSoup
import json, urllib2, re

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
    
    page = BeautifulSoup(urllib2.urlopen(url).read())
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
    
    return project


if __name__ == "__main__":
    url="http://www.donorschoose.org/donors/proposal.html?id=569177"
    p=parse_proj_page(url)
    print json.dumps(p)
