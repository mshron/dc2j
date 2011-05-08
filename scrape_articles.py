from BeautifulSoup import BeautifulSoup
import urllib
import placefinder

url = "http://shrewsbury.net/"
def get_top_articles(url):
    handle = urllib.urlopen(url)
    soup = BeautifulSoup(''.join(handle.read()))
    links = soup.findAll('a')
    out = []
    for link in links:
        try:
            if url in link['href']:
                out.append(link['href'])
        except KeyError:
            pass
    return out 

def find_article_text(url, min_chars = 200):
    handle = urllib.urlopen(url)
    soup = BeautifulSoup(''.join(handle.read()))
    paragraphs = soup.findAll('p')
    return ' '.join([p.text for p in paragraphs if len(p.text)>min_chars])

links = get_top_articles(url)
names_re = placefinder.make_re()

for link in links:
    text = find_article_text(link)
    try:
        print placefinder.names(names_re, text)
        print text
        print "\n"
    except IndexError:
        pass
