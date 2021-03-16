import feedparser
from flask import Flask, request, render_template, jsonify, Markup,redirect,url_for
import time
import threading
from apscheduler.schedulers.background import BackgroundScheduler

from fueldb import searchServo,recordPrices,nearByServo,getSuburbs,checkPricesExist
import fuelwatch_codes as fc
from fuelData import tomorrowReleased,tomorrow
from htmlBuilder import fuelTable
from userData import UserData

app = Flask(__name__)

user = UserData()
searchResult = {}
suburbs = '["' + '","'.join(getSuburbs()) + '"]' 

@app.route('/get_location')
def getUserLocation():
    user.latlng = (request.args.get('lat'), request.args.get('lng'))
    user.updateLocation()
    return redirect(url_for('buildPage'))

@app.route('/search', methods=['GET', 'POST'])
def searchForm():
    if request.method == "POST":
        searchResult.clear()
        searchResult.update(request.form.to_dict())

    return redirect(url_for('buildPage'))

@app.route('/')
@app.route('/index')
def buildPage():

    radiusChoices = [2,3,5,10,15]
    radius = 5
    limit = 5

    if('radius' in request.args):
        radius = int(request.args['radius'])

    #Lookups are expensive so we do this once to get the servos close to the user and then pass that data.
    servos = nearByServo(Latlng=user.latlng, Distance=radius)
    return render_template('index.html',
        RadiusChoices = radiusChoices,
        Radius = radius,
        UserLocation = user.location.raw['address']['suburb'],
        Suburbs = suburbs,
        Regions = fc.Regions,
        StateRegions = fc.StateRegions,
        Brands = fc.FuelBrands,
        ULP = Markup(fuelTable(searchServo(Near=servos,Limit=limit))),
        PULP = Markup(fuelTable(searchServo(Product=2,Near=servos,Limit=limit))),
        RON98 = Markup(fuelTable(searchServo(Product=6,Near=servos,Limit=limit))),
        DIESEL = Markup(fuelTable(searchServo(Product=4,Near=servos,Limit=limit))),
        LPG = Markup(fuelTable(searchServo(Product=5,Near=servos,Limit=limit))),
        TMRW_ULP = None if not tomorrowReleased() else Markup(fuelTable(searchServo(Date=tomorrow(),Near=servos,Limit=limit))),
        TMRW_PULP = None if not tomorrowReleased() else Markup(fuelTable(searchServo(Product=2,Date=tomorrow(),Near=servos,Limit=limit))),
        TMRW_RON98 = None if not tomorrowReleased() else Markup(fuelTable(searchServo(Product=6,Date=tomorrow(),Near=servos,Limit=limit))),
        TMRW_DIESEL = None if not tomorrowReleased() else Markup(fuelTable(searchServo(Product=4,Date=tomorrow(),Near=servos,Limit=limit))),
        TMRW_LPG = None if not tomorrowReleased() else Markup(fuelTable(searchServo(Product=5,Date=tomorrow(),Near=servos,Limit=limit))),
        Search_result = None if searchResult == {} else Markup(fuelTable(searchServo(**searchResult,Limit=20)))
    )


if __name__ == '__main__':

    recordPrices(True)
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(func=recordPrices, trigger="cron", hour=14, minute=31)
    sched.start()
    
    app.run(debug=True, host='0.0.0.0')