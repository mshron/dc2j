#!/usr/bin/env python

# -*- coding: latin-1 -*-

from BeautifulSoup import BeautifulSoup
#import glob
import placefinder
import csv
import sys
import numpy as np
import logging
import os

def find_article_text(file, min_chars = 200):
    logging.debug('extracting article text for %s'%file.name)
    soup = BeautifulSoup(''.join(file.read()))
    paragraphs = soup.findAll('p')
    return ' '.join([p.text for p in paragraphs if len(p.text)>min_chars])

def get_placenames(files, place_re, max_files=100):
    out = []
    i = 0
    for file in files:
        logging.debug('looking for places in file: %s'%file)
        if i>max_files: break
        try:
            _f = open(file)
        except:
            logging.warn('failed to open %s'%file)
            continue
        text = find_article_text(_f)
        try:
            names = placefinder.names(place_re,text)
            logging.debug("found %s"%names)
            out.append(names)
        except IndexError:
            continue
        i += 1
    return out

def parse_location_file(filename="places_manymore_locations.psv"):
    logging.info('parsing location file....')
    reader = csv.reader(open(filename, 'r'), delimiter='|')
    places = {}
    for line in reader:
        l = places.setdefault(line[0], [])
        l.append((float(line[1]),float(line[2])))
    return places

def coordinates(_names, places):
    logging.info("getting coordinates for the set of extracted places")
    out = []
    flat_names = reduce(lambda x,y: x+y, reduce(lambda x,y: x+y, _names))
    print flat_names
    names = filter(lambda x: len(x)>0, flat_names)
    for name in names:
        out.append(places[name]) 
    return out

def nearest(pt, list):
    """
    >>> nearest([0,0], [[1,1],[2,2],[3,5]])
    [1, 1]
    """
    logging.info('calculating nearest point to' + str(pt))
    distance = lambda (lat,lon): abs(pt[0]-lat)+abs(pt[1]-lon)
    d_sort = lambda a,b: int(distance(a)-distance(b))
    closest = sorted(list, cmp=d_sort)[0]
    return closest

def coverage(center, points):
    logging.info('finding coverage around %s'%str(center))
    _d = np.abs(np.asarray(center)-np.asarray(points))
    d_lat = [d for d in _d[:,0] if d < 2]
    d_lon = [d for d in _d[:,1] if d < 3]
    return [np.median(d_lat), np.median(d_lon)]

def dir_walker_callback(arg, dirname, fnames):
    for fname in fnames:
        if fname.endswith('html'):
            arg.append(dirname+os.path.sep+fname)

def get_newspaper_webpages(dir):
    files = []
    assert os.path.isdir(dir), dir
    os.path.walk(dir, dir_walker_callback, files)
    print files
    return files

def run_on(dirs, pts):
    places = parse_location_file()
    place_re = placefinder.make_re(places)
    sys.stderr.write('Created place regexp.\n')
    
    covs = []
    for dir, pt in zip(dirs, pts):
        dir = "/Users/mike/Dropbox/Projects/dc2j/"+dir.strip()
        logging.info("getting files for directory: %s"%dir)
        files = get_newspaper_webpages(dir)
        names = get_placenames(files, place_re, 100)
        try:
            c = coordinates(names, places)
            n = lambda l: nearest(pt, l)
            c_nearest = map(n, c)
            cov = coverage(pt, c_nearest)
            covs.append(cov)
        except TypeError:
            covs.append((0,0))
        except:
            print names
            raise
    return covs

def main():
    dirs = [
      'www.broomfieldenterprise.com',
      'www.poughkeepsiejournal.com',
      'www.aspendailynews.com',
      'www.suntimes.com',
      'www.southbendtribune.com'
    ]
    pts = [
      (39.9205411,-105.0866504),
      (41.7003713,-73.9209701),
      (39.1910983,-106.8175387),
      (41.887610,-87.636057),
      (41.6725, -86.255278)
    ]
    run_on(dirs, pts)

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    
    from addr2latlon import addr2latlon
    lat, lng = addr2latlon("%s, %s, Newspaper"%("Moline Daily Dispatch", "IL"))
    covs = run_on(['www.qconline.com'],[(lat,lng)])
    print "-------\n" + str(covs)
