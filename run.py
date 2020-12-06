import feedparser
from workers import getFuelData,filterData
from htmlBuilder import header,fuelTable,footer
from pprint import pprint
from flask import Flask

'''
    Show opening page
    Collect data. 
        ?Could this be done twice per day and stored locally for faster lookup?
        Better yet, retrieve once, after 2:30pm but use the data for tomorrow as well.
    Show progress e.g. retrieving data, acquiring location, locating closest options
    Reload page with data
'''

app = Flask(__name__)

@app.route('/')
def buildPage():
    scrapedData = getFuelData()

    return f'''
        {header()}
            <div class="heading">FuelWatch</div>
            {fuelTable(filterData(scrapedData, parameters={'Count':3}))}
            {fuelTable(filterData(scrapedData, parameters={'Count':3,'FuelType':'Premium Unleaded'}))}
            {fuelTable(filterData(scrapedData, parameters={'Count':3,'FuelType':'98 RON'}))}
            {fuelTable(filterData(scrapedData, parameters={'Count':3,'FuelType':'Diesel'}))}
            {fuelTable(filterData(scrapedData, parameters={'Count':3,'FuelType':'LPG'}))}
        {footer()}
    '''

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')