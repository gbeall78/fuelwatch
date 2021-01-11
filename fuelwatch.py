import feedparser
from fuelData import FuelData
from workers import userData
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

@app.route('/get_location')
def getUserLocation():
    userData['lng'] = request.args.get('lng')
    userData['lat'] = request.args.get('lat')
    return redirect(url_for('buildPage'))

@app.route('/')
@app.route('/index')
def buildPage():

    if userData['lng'] != '':
        print(userData['lng'])
    else:
        print('Gathering data')

    return render_template('index.html',
        ULP = Markup(fuelTable(today.filterData(parameters={'Count':3}))),
        PULP = Markup(fuelTable(today.filterData(parameters={'Count':3,'FuelType':'Premium Unleaded'}))),
        RON98 = Markup(fuelTable(today.filterData(parameters={'Count':3,'FuelType':'98 RON'}))),
        Diesel = Markup(fuelTable(today.filterData(parameters={'Count':3,'FuelType':'Diesel'}))),
        LPG = Markup(fuelTable(today.filterData(parameters={'Count':3,'FuelType':'LPG'})))
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