from exceptions import invalidStyleParameter,invalidClassParameter,noTableHeaderException,tableHeaderDataSizeMismatchException
from pprint import pprint
import workers
from htmlBuilder import buildTable
from flask import Flask
import pytest

app = Flask(__name__)

def test_buildTable():
    testDataHeader = ["Price", "Trading Name", "Address", "Location"]
    testDataServo = [
        {'price' : "1.05",
        'trading-name' : '7-eleven Balcatta',
        'address' : '1 Fake Street',
        'location' : 'Balcatta'},
        {'price' : "2.05",
        'trading-name' : '9-eleven Balcatta',
        'address' : '2 Fake Street',
        'location' : 'Balcatta'},
    ]

    #Weird style
    with pytest.raises(invalidStyleParameter):
        buildTable(testDataHeader, testDataServo, style="test:test:test")

    #missing ;
    with pytest.raises(invalidStyleParameter):
        buildTable(testDataHeader, testDataServo, style="test:test")
    with pytest.raises(invalidStyleParameter):
        buildTable(testDataHeader, testDataServo, style="test:test; test2:test2")
    with pytest.raises(invalidStyleParameter):
        buildTable(testDataHeader, testDataServo, style="test:test test2:test2")
    
    #Valid style
    buildTable(testDataHeader, testDataServo, style="test:test;")

    #Bad class name
    with pytest.raises(invalidClassParameter):
        buildTable(testDataHeader, testDataServo, style="test:test;", className="34")
    with pytest.raises(invalidClassParameter):
        buildTable(testDataHeader, testDataServo, style="test:test;", className="w-ord")
        
    #valid class name
    buildTable(testDataHeader, testDataServo, style="test:test;", className="_word")
    buildTable(testDataHeader, testDataServo, style="test:test;", className="word")
            

    #Too few items
    with pytest.raises(noTableHeaderException):
        buildTable([], testDataServo)

    #Too many items
    with pytest.raises(tableHeaderDataSizeMismatchException):
        buildTable(testDataHeader+testDataHeader, testDataServo)

def getFuelDataTest():
    fuelData = list()
    fuelData = workers.getFuelData()

    daysCollected = len(fuelData)
    if(daysCollected == 3):
        pprint("Yesterdays, todays and tomorrows data has been collected.")
    elif(daysCollected == 2 and not workers.tomorrowReleased()):
        pprint("Before 2:30PM. Yesterdays and todays data have been collected.")
    else:
        return None

    return fuelData

@app.route('/')
def filterTest():

    fuelData = getFuelDataTest()
    if(fuelData == None):
        pprint("Invalid fuel data list")
        exit()

    #requiredData = workers.filterData(fuelData)
    #requiredData = workers.filterData(fuelData, parameters={'Count':600})
    #requiredData = workers.filterData(fuelData, parameters={'Day':'Today'})
    #requiredData = workers.filterData(fuelData, parameters={'Day':'yesterday'})
    #requiredData = workers.filterData(fuelData, parameters={'FuelType':'Electric'})
    #requiredData = workers.filterData(fuelData, parameters={'Suburb':'Perth'})
    requiredData = workers.filterData(fuelData, parameters={'FuelType':'Diesel','Day':'yesterday'})
    
    strFT = f'Fuel type: {workers.FuelTypes[requiredData[0]["fuelType"]]}\n{buildTable(["Price","Name","Address","Location"],requiredData)}'
    return strFT
    #print(strFT)
    #print(workers.buildTable(["Price","Name","Address","Location"],requiredData))

if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0')

    #pprint(getPrices())
    #pprint(userLocation().city)
    #buildTableTest()    
    #filterTest()
    
    pprint(workers.nearByServo(workers.FremantleLL,5,workers.filterData(workers.getFuelData())))
