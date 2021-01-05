
from geocoder import ip
from datetime import datetime
import collections
import geopy.distance


PerthLL = (-31.950527,115.860458)
CanningtonLL = (-32.019870,115.933000)
FremantleLL = (-32.056171,115.746941)

userData = {
    'lng':  '',
    'lat': ''
}

def userLocation():
     return ip('me')

def nearByServo(me, distance, data):
    
    return [
        servo
        for servo in data if geopy.distance.distance(me,(servo['latitude'],servo['longitude'])).km < distance
    ]