import urllib
import json

def addr2latlon(addr):
    domain = "http://maps.googleapis.com"
    path = "/maps/api/geocode/json"
    query = {
        "address": addr,
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