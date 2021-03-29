import feedparser
from flask import Flask, request, render_template, jsonify, Markup,redirect,url_for
import time
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from geopy.geocoders import Nominatim

from fueldb import searchServo,recordPrices,nearByServo,getSuburbs,checkPricesExist
import fuelwatch_codes as fc
from fuelData import tomorrowReleased,tomorrow
from htmlBuilder import fuelTable

import logging

logging.basicConfig(filename="./fuelwatch.log")
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

app = Flask(__name__)

limit = 5
suburbs = '["' + '","'.join(getSuburbs()) + '"]' 

def getUserLocationData(*args, **kwargs):
    userLatlng = kwargs['LatLng'] if 'LatLng' in kwargs else (-31.950527, 115.860458)
    servos = nearByServo(
        Latlng = userLatlng,
        Distance = kwargs['Radius'] if 'Radius' in kwargs else 5
    )

    if tomorrowReleased():
        tomorrowData = (
                Markup(fuelTable(searchServo(Date=tomorrow(),Near=servos,Limit=limit))) +
                Markup(fuelTable(searchServo(Product=2,Date=tomorrow(),Near=servos,Limit=limit))) +
                Markup(fuelTable(searchServo(Product=6,Date=tomorrow(),Near=servos,Limit=limit))) +
                Markup(fuelTable(searchServo(Product=4,Date=tomorrow(),Near=servos,Limit=limit))) +
                Markup(fuelTable(searchServo(Product=5,Date=tomorrow(),Near=servos,Limit=limit)))
        )
    else:
        tomorrowData = Markup('<h3>Tomorrows prices will be released after 2:30pm WAST.</h3>')

    todayData = (
        Markup(fuelTable(searchServo(Near=servos,Limit=limit))) +
        Markup(fuelTable(searchServo(Product=2,Near=servos,Limit=limit))) +
        Markup(fuelTable(searchServo(Product=6,Near=servos,Limit=limit))) +
        Markup(fuelTable(searchServo(Product=4,Near=servos,Limit=limit))) +
        Markup(fuelTable(searchServo(Product=5,Near=servos,Limit=limit)))
    )

    locator = Nominatim(user_agent="myGeocoder")
    return {
        'today':todayData,
        'tomorrow':tomorrowData, 
        'suburb' : locator.reverse(userLatlng).raw['address']['suburb']
    }

@app.route('/get_location', methods=['GET'])
def getLocation():
    print("Get Location called.")
    print("Radius:" + str(request.args['radius']))
    print("LatLng: " + request.args.get('lat') + " " + request.args.get('lng'))
    return jsonify(getUserLocationData(
        LatLng = (request.args.get('lat'), request.args.get('lng')),
        Radius = int(request.args['radius']) if 'radius' in request.args else None
    ))

@app.route('/search', methods=['GET', 'POST'])
def searchForm():
    if request.method == "POST":
        searchResult = request.form.to_dict()
        return Markup(fuelTable(searchServo(**searchResult,Limit=20)))
    

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def buildPage():
    radius = 5
    radiusChoices = [2,3,5,10,15]

    initData = getUserLocationData()
    return render_template('index.html',
        RadiusChoices = radiusChoices,
        Radius = radius,
        Suburbs = suburbs,
        Regions = fc.Regions,
        StateRegions = fc.StateRegions,
        Brands = fc.FuelBrands,
        Today = initData['today'],
        Tomorrow = initData['tomorrow'],
)

recordPrices(True)
sched = BackgroundScheduler(daemon=True)
sched.add_job(recordPrices, 'cron', hour=14, minute="30-40/2", second=30)
sched.start()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')