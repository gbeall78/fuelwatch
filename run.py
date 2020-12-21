import feedparser
from workers import getFuelData,filterData,userData
from htmlBuilder import fuelTable
from pprint import pprint
from flask import Flask, request, render_template, jsonify, Markup,redirect,url_for

'''
    Show opening page
    Collect data. 
        ?Could this be done twice per day and stored locally for faster lookup?
        Better yet, retrieve once, after 2:30pm but use the data for tomorrow as well.
    Show progress e.g. retrieving data, acquiring location, locating closest options
    Reload page with data
'''



app = Flask(__name__)

@app.route('/get_location')
def getUserLocation():
    userData['lng'] = request.args.get('lng')
    userData['lat'] = request.args.get('lat')
    return redirect(url_for('/'))


@app.route('/')
def buildPage():
    scrapedData = getFuelData()

    if userData['lng'] != '':
        print(userData['lng'])
    else:
        print('Gathering data')

    return render_template('index.html',
    ULP = Markup(fuelTable(filterData(scrapedData, parameters={'Count':3}))),
    PULP = Markup(fuelTable(filterData(scrapedData, parameters={'Count':3,'FuelType':'Premium Unleaded'}))),
    RON98 = Markup(fuelTable(filterData(scrapedData, parameters={'Count':3,'FuelType':'98 RON'}))),
    Diesel = Markup(fuelTable(filterData(scrapedData, parameters={'Count':3,'FuelType':'Diesel'}))),
    LPG = Markup(fuelTable(filterData(scrapedData, parameters={'Count':3,'FuelType':'LPG'})))
    )

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')