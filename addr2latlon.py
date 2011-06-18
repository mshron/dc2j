import urllib
import json

def addr2latlon(addr):
    domain = "http://maps.googleapis.com"
    path = "/maps/api/geocode/json"
    query = {
        "address": addr,
        "sensor": "false"
    }
    a = json.loads(
        urllib.urlopen(
            domain+path+"?"+urllib.urlencode(query)
        ).read()
    )["results"][0]["geometry"]["location"]
    return a['lat'], a['lng']

if __name__ == "__main__":
    addr = "1600 Amphitheatre Parkway, Mountain View, CA"
    print addr2latlon(addr)
    
