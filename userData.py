from geopy.geocoders import Nominatim

class UserData:

    def __init__(self):
        self.latlng = [-31.950527, 115.860458]
        self.updateLocation()
    
    def updateLocation(self):
        locator = Nominatim(user_agent="myGeocoder")
        self.location = locator.reverse(self.latlng)