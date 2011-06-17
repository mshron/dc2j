import re


def names(name_re, s):
    """Finds place names according to regexp name_re"""
    n =  name_re.findall(s)
    place =  filter(lambda x: len(x)>0,n[0])[0]
    return place.lower()

def make_re():
    name_re = re.compile(r'([A-Z][^,.:]+) -|(?:in | from | of | near | at | downtown )([A-Z][^,.:]+)')
    return name_re

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
    >>> names(name_re, 'Reporting live from Shrewsbury town hall')
    'shrewsbury'
    """

if __name__ == "__main__":
    """To run test: python -m doctest %prog"""
    main()
