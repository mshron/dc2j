import urllib
import json
import csv

fh = open('citieslatlon.csv')
reader = csv.reader(fh)
place_dict = dict()
for row in reader:
    state, city, lat, lon = row
    city = ' '.join(city.split(' ')[:-1]).strip()
    place_dict[(state,city)] = (float(lat),float(lon))

def addr2latlon(state,city):
    
    try:
        return place_dict[(state,city)]
    except KeyError:
        #logging.warn("using google (OMG)")
        print (state,city)
        print "using google OMG"
        pass
    
    domain = "http://maps.googleapis.com"
    path = "/maps/api/geocode/json"
    query = {
        "address": "%s, %s"%(city, state),
        "sensor": "false"
    }
    try:
        a = json.loads(
            urllib.urlopen(
                domain+path+"?"+urllib.urlencode(query)
            ).read()
        )["results"][0]["geometry"]["location"]
    except IndexError:
        print json.loads(
            urllib.urlopen(
                domain+path+"?"+urllib.urlencode(query)
            ).read()
        )
        return None
    return a['lat'], a['lng']

if __name__ == "__main__":
    print addr2latlon('OR', 'Culver')