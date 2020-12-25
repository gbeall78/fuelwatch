import exceptions
from feedparser import parse
from pprint import pprint
from geocoder import ip
from datetime import datetime
import collections
import geopy.distance
import os.path
import json

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

PerthLL = (-31.950527,115.860458)
CanningtonLL = (-32.019870,115.933000)
FremantleLL = (-32.056171,115.746941)

userData = {
    'lng':  '',
    'lat': ''
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

def getPrices(day: str, product_id: str, suburb='',  brand='', surrounding=False):
    """Get fuel prices from FuelWatch.WA.gov.au

    Parameters
    ----------
    day : str
        The day to be retrieved. Valid options are yesterday, today and tomorrow
    product_id : str
        The fuel type ID
    suburb : str, optional
        The suburb to get fuel prices for 
    brand : str, optional
        Brand of fuel
    surrounding : bool, optional
        Whether to include surrounding areas to the above suburb (Default is false).
    """

    options = 'Product=' + product_id
    options += '&Day=' + day
    
    if suburb != '':
        options += '&Suburb=' + suburb

    if surrounding:
        options += '&Surrounding=yes'

    return parse('https://www.fuelwatch.wa.gov.au/fuelwatch/fuelWatchRSS?' + options)

def getFuelData():
    """Builds a list of fuel data

        Collects yesterdays, todays and (if after 2:30pm) tomorrows fueldata.
    """

    #We only want to get tomorrows data if it's been released
    Day = Days.copy()
    if not tomorrowReleased():
        Day.pop()
    
    #The main data list which will contain for each day, all fueltypes from all service stations.
    data = list()

    for d in Day:
        dList = list()

        for ft in FuelTypes:
            fDict = dict()
            fDict['fuelType'] = ft

            #Get this day and fueltypes prices then sort by lowest price
            scrape = list()
            scrape = getPrices(day=d,product_id=str(ft))
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
            dList.append(fDict)
        data.append(dList)

    return data

def tomorrowReleased():
    """Check if tomorrows data is released

    Tomorrows fuel data is released after 2:30pm.
    """

    now = datetime.now().time()
    afterToothHurty = now.replace(hour=14, minute=30, second=0, microsecond=0)

    return now > afterToothHurty

def userLocation():
     return ip('me')

def filterData(data, parameters={}):

    '''
    data[
        day[
            fueltype{
                Type,
                stations[
                    station {}
                }
            ]
        ]
    ]

    data[day=0[fueltype=1[stations=5{station}]]]
    '''

    try:
        if 'Day' not in parameters:
            dayIndex = 1
        else:
            dayIndex = Days.index(parameters['Day'])
    except ValueError:
        pprint('Invalid day given. Valid options are yesterday, today or tomorrow')
        exit()

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
    count = len(data[dayIndex][ftIndex]['stations']) 
    if 'Count' in parameters:
        if parameters['Count'] < count:
            count = parameters['Count']

    filterData = list()

    filterData = data[dayIndex][ftIndex]['stations'][0:count]
    return filterData

def nearByServo(me, distance, data):
    
    return [
        servo
        for servo in data if geopy.distance.distance(me,(servo['latitude'],servo['longitude'])).km < distance
    ]

def writeCache(data):
    with open("fuelData.json", "w") as fuelFile:
        json.dump(data, fuelFile)

def readCache():
    if(os.path.isfile("fuelData.json")):
        with open("fuelData.json", "r") as fuelFile:
            return json.load(fuelFile)
    else:
        return ''