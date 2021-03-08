from feedparser import parse
from urllib.parse import quote_plus
from datetime import datetime,timedelta

def getPrices(*args, **kwargs):
    """Get fuel prices from FuelWatch.WA.gov.au

        If an invalid parameter is given it will default to unleaded petrol in the Perth Metro area
    """

    options = ''
    if kwargs.get('Tomorrow'):
        options += '&Day=tomorrow'
   
    if 'Product' in kwargs:
        options += '&Product=' + str(kwargs['Product'])
   
    if 'Suburb' in kwargs:
        options += '&Suburb=' + quote_plus(kwargs['Suburb'])

    if 'Surrounding' in kwargs:
        options += '&Surrounding=' + kwargs['Surrounding']

    if 'Region' in kwargs:
        options += '&Region=' + str(kwargs['Region'])

    if 'StateRegion' in kwargs:
        options += '&StateRegion=' + str(kwargs['StateRegion'])

    return parse('https://www.fuelwatch.wa.gov.au/fuelwatch/fuelWatchRSS?' + options)

def tomorrowReleased():
    """Check if tomorrows data is released

    Tomorrows fuel data is released after 2:30pm.
    """

    now = datetime.now().time()
    afterToothHurty = now.replace(hour=14, minute=30, second=0, microsecond=0)

    return now > afterToothHurty

def tomorrow():
    return (datetime.now() + timedelta(days=1))
