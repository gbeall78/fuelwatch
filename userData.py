from geopy.geocoders import Nominatim

class UserData:

    def __init__(self):
        self.latlng = [-31.950527, 115.860458]
        locator = Nominatim(user_agent="myGeocoder")
        self.location = locator.reverse(self.latlng)
    
    def userSuburb(self):
        return self.location