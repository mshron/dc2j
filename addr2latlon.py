import urllib
import json

fh = open('gazetter.txt')
place_dict = dict()
for line in fh:
    state, city, lat, lon = line.split(',')
    city = ''.join(city.split(' ')[:-1])
    place_dict[(state,city)] = (lat,lon)

def addr2latlon(state,city):
    
    try:
        return place_dict[(state,city)]
    except KeyError:
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
    print addr2latlon("IL")