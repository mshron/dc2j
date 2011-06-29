#import scrape_articles
#from addr2latlon import addr2latlon
import logging
import sys
import urlparse
import urllib
from get_coverage_basic import get_offsets

logging.basicConfig(stream=sys.stdout,level=logging.INFO)

a = [443,623,673,254,362,309,79,636,1363,126,486,440,183,1397,201,339,494,755,707,963,1399,1318,1181,102,1334,588,1206,70,877,130,863,639,355,1290,903,1276,27,1226,459,387,234,1043,107,680,476,386,1161,331,208,1309,1004,85,1163,97,1361,744,886,695,220,192,909,628,872,345,1382,919,979,360,128,565,418,321,551,500,1327,908,227,32,698,4,274,289,699,995,91,96,583,407,763,876]

fh = open('media_top10after5.tab', 'r')
headers = fh.next()
# nid|state|city|name|url|error
todo = []
#logging.info("spidering the newspapers")

for line in fh:
    nid, state, city, newspaper, url, err = line.split('|')
    nid = int(nid)
    if True:#nid in a:
        logging.info("spidering %s"%newspaper)
        if not err.strip():
            url = urlparse.urlparse(url).netloc
            todo.append((nid, newspaper, city, state, url))
            #if not os.path.isdir(url):
            #    cmd = "./spider.sh %s"%url
            #    os.system(cmd)
fh.close()

logging.info("getting locations and offsets")
urls, locns, papers, states, nids, offsets = [], [], [], [], [], []
for nid, newspaper, city, state, url in todo:
    try:
        locn, offset = get_offsets(state,city)
        urls.append(url)
        papers.append(newspaper)
        locns.append(locn)
        offsets.append(offset)
        states.append(state)
        nids.append(nid)
    except ValueError:
        logging.warn("skipping %s (ValueError)"%newspaper)
        continue
    except TypeError:
        logging.warn("skipping %s (TypeError)"%newspaper)
        continue
    except KeyError:
        logging.warn("skipping %s (KeyError)"%newspaper)
        continue

#logging.info("getting coverage bounding boxes")
#centres, offsets = scrape_articles.run_on(urls, locns, states)

logging.info("writing output file")
# write the output file
out = open('newspaper_info.csv', 'w')
out.write('nid, name, url, lat, lng, offsetLat, offsetLng\n')
for i, (nid, paper, url, locn, offset) in enumerate(zip(nids, papers,urls,locns,offsets)):
    out.write(
        "%s,%s,%s,%s,%s,%s,%s\n"
        %(nid, paper, url.strip(), locn[0], locn[1], offset[0], offset[1])
    )
out.close()


for i, (nid, paper, url, locn, offset) in enumerate(zip(nids, papers,urls,locns,offsets)):
    f = urllib.urlopen(
        "http://dc2jpr.appspot.com/data/newspapers", 
        urllib.urlencode({
            "nid":nid,
            "lat":locn[0],
            "lng":locn[1],
            "offsetLat":offset[0],
            "offsetLng":offset[1]
        })
    )
    print f.code
    f.close()

