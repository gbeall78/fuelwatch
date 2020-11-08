import feedparser
import workers
import htmlBuilder
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

    scrapedData = list()
    scrapedData = workers.getFuelData()
    requiredData = workers.filterData(scrapedData, parameters={'Count':3})

    page = f'''
    {htmlBuilder.header()}
    <div>Fuel type: {workers.FuelTypes[requiredData[0]["fuelType"]]}</div>
    {htmlBuilder.buildTable(["Price","Name","Address","Location"],requiredData)}
    {htmlBuilder.footer()}
    '''
    return page

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')