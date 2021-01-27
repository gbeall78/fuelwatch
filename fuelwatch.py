import feedparser
from userData import UserData
from fuelData import FuelData
from htmlBuilder import fuelTable
from flask import Flask, request, render_template, jsonify, Markup,redirect,url_for
import time
import threading
import schedule

app = Flask(__name__)

yesterday = FuelData('yesterday')
today = FuelData('today')
tomorrow = FuelData('tomorrow')
user = UserData()
init()

@app.route('/get_location')
def getUserLocation():
    user.latlng = [request.args.get('lat'), request.args.get('lng')]
    user.updateLocation()
    return redirect(url_for('buildPage'))

@app.route('/')
@app.route('/index')
def buildPage():

    radiusChoices = [2,3,5,10,15]
    radius = 5

    if('radius' in request.args):
        radius = int(request.args['radius'])

    return render_template('index.html',
        radiusChoices = radiusChoices,
        radius = radius,
        UserLocation = user.location.raw['address']['suburb'],
        ULP = Markup(
            fuelTable(
                today.nearByServo(today.filterData(),user.latlng,radius)[0:3]
            )
        ),
        PULP = Markup(
            fuelTable(
                today.nearByServo(today.filterData(parameters={'FuelType':'Premium Unleaded'}),user.latlng,radius)[0:3]
            )
        ),
        RON98 = Markup(
            fuelTable(
                today.nearByServo(today.filterData(parameters={'FuelType':'98 RON'}),user.latlng,radius)[0:3]
            )
        ),
        Diesel = Markup(
            fuelTable(
                today.nearByServo(today.filterData(parameters={'FuelType':'Diesel'}),user.latlng,radius)[0:3]
            )
        ),
        LPG = Markup(
            fuelTable(
                today.nearByServo(today.filterData(parameters={'FuelType':'LPG'}),user.latlng,radius)[0:3]
            )
        ),
        TMRW_ULP = None if tomorrow.data == [] else Markup(
            fuelTable(
                tomorrow.filterData()
            )
        ),
        TMRW_PULP = None if tomorrow.data == [] else  Markup(
            fuelTable(
                tomorrow.filterData(parameters={'FuelType':'Premium Unleaded'})[0:3]
            )
        ),
        TMRW_RON98 = None if tomorrow.data == [] else  Markup(
            fuelTable(
                tomorrow.filterData(parameters={'FuelType':'98 RON'})[0:3]
            )
        ),
        TMRW_Diesel = None if tomorrow.data == [] else  Markup(
            fuelTable(
                tomorrow.filterData(parameters={'FuelType':'Diesel'})[0:3]
            )
        ),
        TMRW_LPG = None if tomorrow.data == [] else  Markup(
            fuelTable(
                tomorrow.filterData(parameters={'FuelType':'LPG'})[0:3]
            )
        ),
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

def renewData():
    yesterday.renew()
    today.renew()
    tomorrow.renew()

def init():
    '''
        Initialise data then set scheduler.
        Scheduler doesn't run missed jobs
    '''

    schedule.every().day.at("00:01").do(renewData)
    schedule.every().day.at("14:31").do(renewData)
    
    stop_run_continuously = run_continuously()

if __name__ == '__main__':
    

    app.run(debug=True, host='0.0.0.0')