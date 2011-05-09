from BeautifulSoup import BeautifulSoup
import urllib
import placefinder
import csv

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
    try:
        handle = urllib.urlopen(url)
    except IOError:
        return None
    soup = BeautifulSoup(''.join(handle.read()))
    paragraphs = soup.findAll('p')
    return ' '.join([p.text for p in paragraphs if len(p.text)>min_chars])

def get_placenames(paper_url, max_urls=100):
    urls = get_top_articles(paper_url)
    names_re = placefinder.make_re()
    out = []
    for url in urls[:max_urls]:
        text = find_article_text(url)
        try:
            out.append(placefinder.names(names_re, text))
        except IndexError:
            pass
    return out

def parse_location_file(filename="places_locations.psv"):
    reader = csv.reader(open(filename, 'r'), delimiter='|')
    places = {}
    for line in reader:
        l = places.setdefault(line[0], [])
        l.append((line[1],line[2]))
    return places

paper_url = "http://shrewsbury.net/"
names = get_placenames(paper_url, max_urls=30)
places = parse_location_file()
points = []
for name in names:
    try:
        points.append(places[name])
    except KeyError:
        pass
