import scrape_articles
from addr2latlon import addr2latlon
import logging
import sys
import os
import urlparse

logging.basicConfig(stream=sys.stdout,level=logging.INFO)

fh = open('papers.tsv', 'r')
todo = []
logging.info("spidering the newspapers")
for i,line in enumerate(fh):
    newspaper, state, url = line.split('\t')
    url = urlparse.urlparse(url).netloc
    todo.append((newspaper, state, url))
    if not os.path.isdir(url):
        cmd = "./spider.sh %s"%url
        os.system(cmd)
fh.close()

logging.info("getting locations")
urls, locns, papers = [], [], []                                               
for newspaper, state, url in todo:    
    try:
        locn = addr2latlon("%s, %s, Newspaper"%(newspaper, state))
        if locn:
            urls.append(url)
            locns.append(locn)
            papers.append(newspaper)
    except ValueError:
        continue
    except TypeError:
        continue

print urls, locns, papers

logging.info("getting coverage bounding boxes")
offsets = scrape_articles.run_on(urls, locns)

# write the output file
out = open('newspaper_info.csv', 'w')
out.write('nid, name, url, lat, lng, offsetLat, offsetLng\n')
for paper, url, locn, offset in zip(papers,urls,locns,offsets):
    out.write(
        "%s,%s,%s,%s,%s,%s,%s\n"
        %(i, newspaper, url.strip(), locn[0], locn[1], offset[0], offset[1])
    )
out.close()