
from geocoder import ip
from datetime import datetime
import collections



PerthLL = (,)
CanningtonLL = (-32.019870,115.933000)
FremantleLL = (-32.056171,115.746941)

userData = {
    'lng':  '',
    'lat': ''
}

def userLocation():
     return ip('me')

