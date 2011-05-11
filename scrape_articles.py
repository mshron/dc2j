#!/usr/bin/env python
# -*- coding: latin-1 -*-

from BeautifulSoup import BeautifulSoup
import glob
import urllib
import placefinder
import csv
import sys
import numpy as np

def find_article_text(file, min_chars = 200):
    soup = BeautifulSoup(''.join(file.read()))
    paragraphs = soup.findAll('p')
    return ' '.join([p.text for p in paragraphs if len(p.text)>min_chars])

def get_placenames(files, place_re, max_files=100):
    out = []
    for i,file in enumerate(files):
        if i>max_files: break
        try:_f = open(file)
        except: continue
        text = find_article_text(_f)
        try:
            out.append(placefinder.names(place_re,text))
        except IndexError:
            pass
    return out

def parse_location_file(filename="places_locations.psv"):
    reader = csv.reader(open(filename, 'r'), delimiter='|')
    places = {}
    for line in reader:
        l = places.setdefault(line[0], [])
        l.append((float(line[1]),float(line[2])))
    return places

def coordinates(_names, places):
    out = []
    flat_names = reduce(lambda x,y: x+y,reduce(lambda x,y: x+y, _names))
    names = filter(lambda x: len(x)>0, flat_names)
    print names
    for name in names:
       out.append(places[name]) 
    return out

def nearest(pt, list):
    """
    >>> nearest([0,0], [[1,1],[2,2],[3,5]])
    [1, 1]
    """
    distance = lambda (lat,lon): abs(pt[0]-lat)+abs(pt[1]-lon)
    d_sort = lambda a,b: int(distance(a)-distance(b))
    closest = sorted(list, cmp=d_sort)[0]
    return closest

def coverage(center, points):
    d = np.abs(np.asarray(center)-np.asarray(points))
    return np.median(d,0)

def recurse_subdirectories(g):
    n = '/*'
    next = glob.glob(g + n)
    sofar = next
    count = 1
    while next != []:
        path = g + n*(count+1)
        count += 1
        next = glob.glob(path)
        sofar.extend(next)
    return sofar

def main():
    files = recurse_subdirectories('www.broomfieldenterprise.com')

    pt = (40.0149856,-105.2705456)

    places = parse_location_file()
    place_re = placefinder.make_re(places)
    sys.stderr.write('Created place regexp.\n')

    names = get_placenames(files, place_re, 50)
    c = coordinates(names, places)
    n = lambda l: nearest(pt, l)
    c_nearest = map(n, c)
    print c_nearest
    cov = coverage(pt, c_nearest)
    print cov


if __name__ == "__main__":
    main()
