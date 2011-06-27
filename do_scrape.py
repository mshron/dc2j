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
    if False:
        if not os.path.isdir(url):
            cmd = "./spider.sh %s"%url
            os.system(cmd)
fh.close()

logging.info("getting locations")
urls, locns, papers, states = [], [], [], []
for newspaper, state, url in todo[:1]:    
    try:
        locn = addr2latlon("%s, %s, Address"%(newspaper, state))
        urls.append(url)
        papers.append(newspaper)
        locns.append(locn)
        states.append(state)            
    except ValueError:
        continue
    except TypeError:
        continue

logging.info("getting coverage bounding boxes")
centres, offsets = scrape_articles.run_on(urls, locns, states)

logging.info("writing output file")
# write the output file
out = open('newspaper_info.csv', 'w')
out.write('nid, name, url, lat, lng, offsetLat, offsetLng\n')
for i, (paper, url, locn, offset) in enumerate(zip(papers,urls,centres,offsets)):
    out.write(
        "%s,%s,%s,%s,%s,%s,%s\n"
        %(i, paper, url.strip(), locn[0], locn[1], offset[0], offset[1])
    )
out.close()
