#!/usr/bin/env python
# -*- coding: latin-1 -*-
import re
from itertools import groupby


def names(name_re, s):
    """Finds place names according to regexp name_re
    >>> r = [re.compile(r'(Los Angeles|New York)')]
    >>> names(r, 'It looks like were in Los Angeles.')
    ['Los Angeles']
    """
    out = []
    for places in name_re:
        hits = places.findall(s)
        for h in hits:
            if len(h) > 0:
                out.append(h)
    return out

def make_re(places, split=75):
    out = []
    p = groupby(enumerate(places.iterkeys()), lambda (i,x): i/split)
    pre_context = '(?: in | from | of | near | at | downtown )'
    for key,place_group in p:
        places = [place[1] for place in place_group]
        pattern = r'%s('%pre_context +\
                  (')|%s('%pre_context).join(places)+\
                  r')'
        r = re.compile(pattern)
        out.append(r)
    return out

def main():
    """
    >>> name_re = make_re()
    >>> names(name_re, 'JUNEAU - What lovely weather!')
    'juneau'
    >>> names(name_re, 'Not from Juneau, Alaska.')
    'juneau'
    >>> names(name_re, 'Live from Gotham City.')
    'gotham city'
    >>> names(name_re, 'Live from Gotham City. Not from Juneau, Alaska.')
    'gotham city'
    >>> t = "SHREWSBURY, Massachusetts – As previously admitted, my morning regimen includes reading the comics while eating breakfast, and awhile ago Dagwood "
    >>> names(name_re, t)
    'shrewsbury'
    >>> names(name_re, 'Reporting live from Shrewsbury town hall')
    'shrewsbury'
    """

if __name__ == "__main__":
    """To run test: python -m doctest %prog"""
    main()
