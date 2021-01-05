import exceptions as e
from feedparser import parse
import collections
from pprint import pprint
import json
from pathlib import Path
from datetime import datetime,timedelta

Days = ['yesterday', 'today', 'tomorrow']

FuelTypes = {
    1 : 'Unleaded Petrol',
    2 : 'Premium Unleaded',
    4 : 'Diesel',
    5 : 'LPG',
    6 : '98 RON',
    10 : 'E85',
    11 : 'Brand diesel',
}
    
FuelBrands = {
    '29' : '7-Eleven',
    '2' : 'Ampol',
    '3' : 'Better Choice',
    '4' : 'BOC',
    '5' : 'BP',
    '6' : 'Caltex',
    '19' : 'Caltex Woolworths',
    '20' : 'Coles Express',
    '32' : 'Costco',
    '24' : 'Eagle',
    '25' : 'FastFuel 24/7',
    '7' : 'Gull',
    '15' : 'Independent',
    '8' : 'Kleenheat',
    '9' : 'Kwikfuel',
    '10' : 'Liberty',
    '30' : 'Metro Petroleum',
    '11' : 'Mobil',
    '13' : 'Peak',
    '26' : 'Puma',
    '14' : 'Shell',
    '23' : 'United',
    '27' : 'Vibe',
    '31' : 'WA Fuels',
    '16' : 'Wesco',
}

class FuelData:

    def __init__(self, day=None):
        for d in Days:
            if day == d:
                self.day = day
        if self.day == None:
            raise AttributeError("FuelData object requires the parameter yesterday, today or tomorrow")

        self.dataStore = {
            'Type': 'File',
            'Root': './data/',
            'File': "fuelData_" + self.day + ".json",
            
        }
        self.dataStore['Location'] = self.dataStore['Root'] + self.dataStore['File']

        self.cacheFile = Path(self.dataStore['Location'])

        self.data = []
        self.renew()

    def __del__(self):
        self.removeCache()
        self.data = []
    
    def renew(self):
        if(not self.writeCache()):
            self.data = self.readCache()

        #Fail if there is no data except for tomorrows data when it hasn't been released.
        if(self.data == []):
            if(self.day == 'tomorrow' and self.tomorrowReleased()):
                raise e.cacheFailureException("Failed to write cache")
            elif(not self.day == 'tomorrow' ):
                raise e.cacheFailureException("Failed to write cache")

    def getPrices(self, product_id: str, suburb='',  brand='', surrounding=False):
        """Get fuel prices from FuelWatch.WA.gov.au

        Parameters
        ----------
        day : str
            The fuel type ID
        suburb : str, optional
            The suburb to get fuel prices for 
        brand : str, optional
            Brand of fuel
        surrounding : bool, optional
            Whether to include surrounding areas to the above suburb (Default is false).
        """

        options = 'Product=' + product_id
        options += '&Day=' + self.day
        
        if suburb != '':
            options += '&Suburb=' + suburb

        if surrounding:
            options += '&Surrounding=yes'

        return parse('https://www.fuelwatch.wa.gov.au/fuelwatch/fuelWatchRSS?' + options)

    def getFuelData(self):
        """Builds a list of fuel data
        Collects fueldata.
        """

        self.data = []

        for ft in FuelTypes:
            fDict = dict()
            fDict['fuelType'] = ft

            #Get this day and fueltypes prices then sort by lowest price
            scrape = list()
            scrape = self.getPrices(product_id=str(ft))
            s=sorted(scrape['items'], key=lambda item : item['price'], reverse=False)

            #Build new list of service station dictionaries containing just the required data
            sList = list()
            for i in s:
                servo = dict()
                servo = {
                    'fuelType' : ft,
                    'price' : i['price'],
                    'brand' : i['brand'],
                    'trading-name' : i['trading-name'],
                    'location' : i['location'],
                    'address' : i['address'],
                    'longitude' : i['longitude'],
                    'latitude' : i['latitude'],
                }
                sList.append(servo)
                
            fDict['stations'] = sList
            self.data.append(fDict)

    def filterData(self, parameters={}):

        try:   

            if 'FuelType' not in parameters:
                ftIndex = 0
            else:
                if parameters['FuelType'] not in FuelTypes.values():
                    raise KeyError

                fv = collections.OrderedDict(sorted(FuelTypes.items()))
                for i,(k,v) in enumerate(fv.items()):
                    if(v == parameters['FuelType']):
                        ftIndex = i

        except KeyError as err:
            pprint('Invalid fuel type given. Valid options are:')
            for i in FuelTypes: 
                pprint(FuelTypes[i])
            exit()
        
        #Check if the requested number of items doesn't exceed the number items that exist.
        #Set count to the lowest option.
        count = len(self.data[ftIndex]['stations']) 
        if 'Count' in parameters:
            if parameters['Count'] < count:
                count = parameters['Count']

        filterData = list()

        filterData = self.data[ftIndex]['stations'][0:count]
        return filterData

    def tomorrowReleased(self):
        """Check if tomorrows data is released

        Tomorrows fuel data is released after 2:30pm.
        """

        now = datetime.now().time()
        afterToothHurty = now.replace(hour=14, minute=30, second=0, microsecond=0)

        return now > afterToothHurty
        
    def writeCache(self):

        '''
            Check if the cache file already exists
            If it does confirm that the file isn't stale data that can be used
            Current data will cause the write to not happen.

            Tomorrows data should also only exist if it's between 1430 and 0000 the next day
            Therefore remove it if it exists outside of that time frame and exit.
        '''

        if(self.cacheFile.exists()):
            dayStart = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            dayEnd = dayStart + timedelta(days=1)
            ytdStart = dayStart + timedelta(days=-1)

            f_ctime = datetime.fromtimestamp(self.cacheFile.stat().st_ctime)

            if(self.day == 'today'):
                if(f_ctime >= dayStart and f_ctime < dayEnd):
                    return False

            elif(self.day == 'yesterday'):
                if(f_ctime > ytdStart):
                    return False
                
            elif(self.day == 'tomorrow'):
                if(self.tomorrowReleased() and f_ctime < dayEnd):
                    return False
                else: #Tomorrow hasn't been released so the file should be removed
                    self.cacheFile.unlink()
                    return True
        #No file exists for Tomorrow but it hasn't been released so exit.
        elif(self.day == 'tomorrow' and not self.tomorrowReleased()):
            return True

        # No valid file found so get the data from FuelWatch and store it.
        self.getFuelData()

        with open(self.dataStore['Location'], "w") as fuelFile:
            json.dump(self.data, fuelFile)
        return True

    def readCache(self):
        if(self.cacheFile.exists()):
            with open(self.dataStore['Location'], "r") as fuelFile:
                return json.load(fuelFile)
        return []