import feedparser
from userData import UserData
from fuelData import FuelData
from htmlBuilder import fuelTable
from flask import Flask, request, render_template, jsonify, Markup,redirect,url_for
import time
import threading
import schedule

'''
    Show opening page
    Collect data. 
        ?Could this be done twice per day and stored locally for faster lookup?
        Better yet, retrieve once, after 2:30pm but use the data for tomorrow as well.
    Show progress e.g. retrieving data, acquiring location, locating closest options
    Reload page with data
'''

app = Flask(__name__)

yesterday = FuelData('yesterday')
today = FuelData('today')
tomorrow = FuelData('tomorrow')
user = UserData()

@app.route('/get_location')
def getUserLocation():
    user.latlng = [request.args.get('lat'), request.args.get('lng')]
    print(user.latlng)
    return redirect(url_for('buildPage'))

@app.route('/')
@app.route('/index')
def buildPage():

    return render_template('index.html',
        UserLocation = user.location.raw['address']['suburb'],
        ULP = Markup(
            fuelTable(
                today.nearByServo(today.filterData(),user.latlng,5)[0:3]
            )
        ),
        PULP = Markup(
            fuelTable(
                today.nearByServo(today.filterData(parameters={'FuelType':'Premium Unleaded'}),user.latlng,5)[0:3]
            )
        ),
        RON98 = Markup(
            fuelTable(
                today.nearByServo(today.filterData(parameters={'FuelType':'98 RON'}),user.latlng,5)[0:3]
            )
        ),
        Diesel = Markup(
            fuelTable(
                today.nearByServo(today.filterData(parameters={'FuelType':'Diesel'}),user.latlng,5)[0:3]
            )
        ),
        LPG = Markup(
            fuelTable(
                today.nearByServo(today.filterData(parameters={'FuelType':'LPG'}),user.latlng,5)[0:3]
            )
        ),
        TMRW_ULP = None if tomorrow.data == [] else Markup(fuelTable(tomorrow.filterData(parameters={'Count':3}))),
        TMRW_PULP = None if tomorrow.data == [] else  Markup(fuelTable(tomorrow.filterData(parameters={'Count':3,'FuelType':'Premium Unleaded'}))),
        TMRW_RON98 = None if tomorrow.data == [] else  Markup(fuelTable(tomorrow.filterData(parameters={'Count':3,'FuelType':'98 RON'}))),
        TMRW_Diesel = None if tomorrow.data == [] else  Markup(fuelTable(tomorrow.filterData(parameters={'Count':3,'FuelType':'Diesel'}))),
        TMRW_LPG = None if tomorrow.data == [] else  Markup(fuelTable(tomorrow.filterData(parameters={'Count':3,'FuelType':'LPG'}))),
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

if __name__ == '__main__':
    
    '''
        Initialise data then set scheduler.
        Scheduler doesn't run missed jobs
    '''

    schedule.every().day.at("00:01").do(renewData)
    schedule.every().day.at("14:31").do(renewData)
    
    stop_run_continuously = run_continuously()

    app.run(debug=True, host='0.0.0.0')