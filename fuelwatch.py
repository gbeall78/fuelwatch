import feedparser
from flask import Flask, request, render_template, jsonify, Markup,redirect,url_for
import time
import threading
import schedule

from fueldb import searchServo,recordPrices,nearByServo,getSuburbs
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

def run_continuously(interval=1):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.

    Source: https://schedule.readthedocs.io/en/latest/background-execution.html
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run

def init():
    '''
        Initialise data then set scheduler.
        Scheduler doesn't run missed jobs
    '''

    schedule.every().day.at("14:31").do(recordPrices)
    
    stop_run_continuously = run_continuously()

if __name__ == '__main__':
    init()
    app.run(debug=True, host='0.0.0.0')