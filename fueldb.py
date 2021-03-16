import sqlite3
import csv
from pathlib import Path
from datetime import datetime,timedelta
import geopy.distance

import fuelwatch_codes as fc
from fuelData import getPrices,tomorrowReleased,tomorrow
from exceptions import databaseTableException

from pprint import pprint as p
import cProfile
import time

"""
.. module:: fueldb.py
   :synopsis: Database operations for the Fuelwatch program

.. moduleauthor:: Glenn Beall <glenn@beall.id.au>

"""

def connectDB(func):
    """Decorator to control database is opened and closed when called
    """

    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('db/fuelwatch.db')
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            kwargs['Cursor'] = conn.cursor()
            rv = func(*args, **kwargs)
        except Exception:
            raise
        else:
            conn.commit()
        finally:
            conn.close()
        return rv
    return wrapper

@connectDB
def dbDataCheck(*args, **kwargs):
    """Check database integrity.

        Currently only checks if tables exist with some data within and not the integrity of the data.
        raises: databaseTableException on error.
        returns: True if passed.
    """

    c = kwargs['Cursor']

    if next(c.execute('SELECT count(*) FROM state_region;'))[0] != len(fc.StateRegions):
        raise databaseTableException('State Region table has insufficient data')

    if next(c.execute('SELECT count(*) FROM region;'))[0]  != len(fc.Regions):
        raise databaseTableException('Region table has insufficient data')

    if next(c.execute('SELECT count(*) FROM brand;'))[0]  != len(fc.FuelBrands):
        raise databaseTableException('Brand table has insufficient data')

    if next(c.execute('SELECT count(*) FROM fuel_type;'))[0]  != len(fc.FuelTypes):
        raise databaseTableException('Fuel_Type table has insufficient data')

    if next(c.execute('SELECT count(*) FROM suburb;'))[0]  == 0:
        raise databaseTableException('Suburb table has insufficient data')

    if next(c.execute('SELECT count(*) FROM surrounding;'))[0]  == 0:
        raise databaseTableException('Surrounding table has insufficient data')

    if next(c.execute('SELECT count(*) FROM servo;'))[0]  == 0:
        raise databaseTableException('Servo table has insufficient data')

    if next(c.execute('SELECT count(*) FROM price;'))[0]  == 0:
        raise databaseTableException('Price table has insufficient data')

    return True

@connectDB
def initFuelwatchDB(*args, **kwargs):
    """Sets up the database schema and records the current day of prices.

        WARNING: Running this function will wipe the database of existing data.
    """
    c = kwargs['Cursor']
    schema = Path('db/schema.sql')

    #Build tables
    if schema.exists():
        c.executescript(schema.read_text())

    #Populate values for state regions, regions and brands
    c.executemany('INSERT INTO state_region(state_region_id, state_region_name) VALUES (?, ?);', list(fc.StateRegions.items()))
    c.executemany('INSERT INTO region(region_id, region_name) VALUES (?, ?);',list(fc.Regions.items()))
    c.executemany('INSERT INTO fuel_type(fuel_id, fuel_name) VALUES (?, ?);',list(fc.FuelTypes.items()))
    c.executemany('INSERT INTO brand(brand_id, brand_name) VALUES (?, ?);',list(fc.FuelBrands.items()))

    '''
    Cycle though all state regions to:
        -Populate suburb table
        -Associate suburb with state region
        -Populate all servos associated with that suburb
    Only ULP data is stored for this run.
    '''

    for sr in fc.StateRegions:
        data = getPrices(StateRegion=sr)
        for servo in data['items']:
            suburb = servo['location'].title()
            c.execute('INSERT OR IGNORE INTO suburb(suburb_name,state_region_id) VALUES(?,?);', (suburb, sr))
            suburbID = next(c.execute('SELECT suburb_id FROM suburb WHERE suburb_name=?', [suburb]))[0]
            brandID = next(c.execute('SELECT brand_id FROM brand WHERE brand_name=?', [servo['brand']]))[0]
            c.execute(
                'INSERT INTO servo(servo_name, servo_address,servo_phone,suburb_id,latitude,longitude,brand_id) VALUES(?,?,?,?,?,?,?);',
                (
                    servo['trading-name'],
                    servo['address'],
                    servo['phone'],
                    suburbID,
                    servo['latitude'],
                    servo['longitude'],
                    brandID,
                )
            )
    
    #Association suburb with regions.
    for r in fc.Regions:
        data = getPrices(Region=r)
        for servo in data['items']:
            c.execute('UPDATE suburb SET region_id=? WHERE region_id IS NULL AND suburb_name=?;', (r, servo['location'].title()))

    #Create surrounding suburb association
    print("This will take some time.")
    for s in c.execute('SELECT suburb_name FROM suburb;').fetchall():
        suburb = s[0]   #Grab first tuple value
        data = getPrices(Suburb=suburb)
        neighbours = list(set([     #Convert to set for uniqueness
            n['location'].title()
            for n in data['items'] if n['location'] != suburb.upper()
        ]))

        for neighbour in neighbours:
            c.execute('''
                INSERT INTO surrounding(suburb_id,neighbour_id) 
                VALUES(
                    (SELECT suburb_id FROM suburb WHERE suburb_name=?),
                    (SELECT suburb_id FROM suburb WHERE suburb_name=?)
                );''', (suburb,neighbour))

    #Record today's prices
    recordPrices(True)

@connectDB
def recordPrices(*args, **kwargs):
    """Records the prices today or tomorrow.

        :param bool args[0]: If args[0] is True then get today's prices
        :return True on success
    """

    c = kwargs['Cursor']
    servos = c.execute('Select servo_name,servo_id from servo;').fetchall()

    if args and args[0]:
        getTomorrow = False
        date = datetime.now().strftime('%Y-%m-%d')
    else:
        if tomorrowReleased():
            getTomorrow = True
            date = tomorrow().strftime('%Y-%m-%d')
        else:
            return False

    #If data already exists dont continue
    if c.execute('SELECT count(*) FROM price where price_date=?;', [date]).fetchone()[0]:
        return False

    '''
        For each fuel type get data from all regions.
        Check each data item against the list of servos
        On match add fuel price details

        TODO - find a more efficient way of doing the servo lookups
    '''

    for ft in fc.FuelTypes:
        for sr in fc.StateRegions:
            data = getPrices(Product=ft,StateRegion=sr,Tomorrow=getTomorrow)
            for d in data['items']:
                for servo in servos:
                    if servo[0] == d['trading-name']:
                        c.execute('''
                            INSERT INTO price(price_date,price,fuel_id,servo_id) 
                            VALUES(?, ?, ?, ?);
                        ''', (date, d['price'], ft, servo[1]))

    return True

@connectDB
def nearByServo(*args, **kwargs):
    """Returns services stations near by
    
        :param LatLng: The Latitude and Longitude to search from.
        :type LatLng: tuple(int, int)
        :param int Distance: Distance from LatLng a service station is considered nearby, in KM. Default is 5KM
        :return servoID: ID's for all service stations within the given distance.
        :rtype list(int)
    """

    c = kwargs['Cursor']

    if 'Latlng' in kwargs:
        if type(kwargs['Latlng']) is not tuple:
            raise TypeError('Latlng must be a tuple')
        
        #Default distance if not specified or invalid distance given
        distance = 5    
        if type(kwargs.get('Distance')) is int:
            distance = kwargs['Distance']

        #latLng = c.execute('Select latitude,longitude from servo;').fetchall()
        latLng = c.execute('Select latitude,longitude from servo ss inner join suburb sb on sb.suburb_id=ss.suburb_id inner join state_region r on r.state_region_id=sb.state_region_id  where sb.state_region_id=98;').fetchall()
        servos = [servo for servo in latLng if geopy.distance.distance(kwargs['Latlng'],servo,).km <= distance]
        
        servoID = []
        for servo in servos:
            servoID += c.execute('SELECT servo_id FROM servo WHERE latitude=? AND longitude=?;',servo).fetchone()
        return servoID

@connectDB
def getServoID(*args, **kwargs):
    r"""Returns a list of Service station IDs

        :param \*args1: List of suburb IDs. If not given all service station IDs will be returned.
        :type \*args1: list(int)
        :return servoID: List of service station IDs
        :rtype list(int)
        
    """

    c = kwargs['Cursor']
    servoID = []

    if args and args[0]:
        for sID in args[0]: 
            servoID += c.execute('Select servo_id FROM servo WHERE suburb_id=?;',[sID[0]]).fetchall()
    else:
        servoID = c.execute('Select servo_id FROM servo;').fetchall()
    return tupleFirst(servoID)

@connectDB
def getSuburbs(*args, **kwargs):
    """Return all suburb names"""
    return tupleFirst(kwargs['Cursor'].execute('Select suburb_name FROM suburb;').fetchall())

def tupleFirst(*args, **kwargs):
    r""" Returns the first item in a list of tuples

        :param \*args1: List of tuples
        :type \*args1: list(tuple())
        :rtype list()
    """

    return [i[0] for i in args[0] if args and args[0] and type(args[0][0]) is tuple]

@connectDB
def searchServo(*args, **kwargs):
    """Search the database for service stations based on the given parameters

    kwargs:
        Product (int): Fueltype to search for, default to Unleaded Petrol (1)
        Limit (int): Maximum number of records to return, default to 5.
        Near (list(servoID)): list of service station IDs that are nearby. This is is determined externally for performance.
        Suburb (str): Suburb name to search for.
        Surrounding (bool): If given then include surrounding suburbs
        Region (int): Region ID to lookup
        StateRegion (int): State Region ID to lookup
        Date (DateTime): Date to search, default to today
        Brand (int): Brand ID to lookup

    Returns: 
        searchData (list(dict())): List containing details about the service stations that meet the search criteria.
    """

    c = kwargs['Cursor']

    servoID = []
    query = []
    join = []

    product = kwargs.get('Product',1)
    limit = kwargs.get('Limit',5)

    if 'Near' in kwargs:
        servoID = kwargs['Near']
    elif kwargs.get('Suburb'):
        suburbs = [kwargs['Suburb']]
        if kwargs.get('Surrounding'):
            suburbs += [ suburb[0] for suburb in c.execute('''
                SELECT n.suburb_name 
                FROM suburb s 
                    INNER JOIN surrounding r ON r.suburb_id = s.suburb_id 
                    INNER JOIN suburb n ON r.neighbour_id = n.suburb_id 
                WHERE s.suburb_name=?;
            ''', [kwargs['Suburb']]).fetchall()]
        query = 'SELECT suburb_id FROM suburb WHERE suburb_name IN ({})'.format(','.join('?' * len(suburbs)))
        servoID = getServoID(c.execute(query,suburbs).fetchall())
    elif kwargs.get('Region'):
        servoID = getServoID(c.execute('''
            SELECT suburb_id 
            FROM suburb sb
                INNER JOIN region r on r.region_id=sb.region_id 
            WHERE sb.region_id=?;'''
            ,[kwargs['Region']]).fetchall())
    elif kwargs.get('StateRegion'):
        servoID = getServoID(c.execute('''
            SELECT suburb_id 
            FROM suburb sb
                INNER JOIN state_region sr on sr.state_region_id=sb.state_region_id 
            WHERE sb.state_region_id=?;'''
            ,[kwargs['StateRegion']]).fetchall())
    else:
        servoID = getServoID()


    date = datetime.now().strftime('%Y-%m-%d')
    if 'Date' in kwargs and isinstance(kwargs['Date'], datetime):
        date = kwargs['Date'].strftime('%Y-%m-%d')

    brand = ''
    if kwargs.get('Brand'):
        brand = ' AND sr.brand_id=?'
        params = servoID + [product, date, kwargs['Brand'], limit]
    else:
        params = servoID + [product, date, limit]

    query = '''
        SELECT p.price,sr.servo_name,sb.suburb_name,sr.servo_address,sr.longitude,sr.latitude,b.brand_name
            FROM servo sr
                INNER JOIN suburb sb ON sb.suburb_id = sr.suburb_id
                INNER JOIN price p ON p.servo_id = sr.servo_id
                INNER JOIN fuel_type f ON f.fuel_id = p.fuel_id 
                INNER JOIN brand b ON b.brand_id = sr.brand_id 
            WHERE 
                sr.servo_id IN ({}) AND f.fuel_id=? AND p.price_date=? {}
            ORDER BY p.price
            LIMIT ?;
            '''.format(','.join('?' * len(servoID)), brand)
    
    lookup = c.execute(query, params).fetchall()

    searchData = []
    for l in lookup:
        searchData.append({'fuelType' : product, 'price' : l[0], 'trading-name' : l[1], 
            'location' : l[2], 'address' : l[3], 'longitude' : l[4], 'latitude' : l[5]})
    
    return searchData

@connectDB
def checkPricesExist(*args, **kwargs):
    r"""Check if there are prices for the given day

        :param datetime \*args: Date to check if prices exist
        :return
    """

    c = kwargs['Cursor']

    if args and args[0] and isinstance(args[0], datetime):
        date = args[0].strftime('%Y-%m-%d')
    else:
        date = datetime.now().strftime('%Y-%m-%d')
    
    return c.execute('SELECT count(*) FROM price where price_date=?;', [date]).fetchone()[0]

if __name__ == '__main__':

    #Running module by itself will record todays and tomorrows prices

    if(not checkPricesExist()):
        recordPrices(True)

    if(not checkPricesExist(tomorrow())):
        if tomorrowReleased():
            recordPrices()
