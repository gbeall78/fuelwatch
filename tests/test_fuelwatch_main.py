import pytest
from workers import filterData,getFuelData,tomorrowReleased
from flask import Flask

app = Flask(__name__)

def test_getFuelData():
    daysCollected = len(getFuelData())

    #If nothing returned fail
    assert daysCollected != None

    #Check if the relevant number of days is collected
    assert daysCollected == 3, "Yesterdays, todays and tomorrows data has been collected."
    assert daysCollected == 2 and not tomorrowReleased(), "Before 2:30PM. Yesterdays and todays data have been collected."

def test_filterData():
    fuelData = getFuelData()

    #requiredData = filterData(fuelData)
    
    #Test too many stations requested
    count = len(fuelData[1][0]['stations']) 
    assert len(filterData(fuelData, parameters={'Count':600})[1][0]['stations']) == count

    #Test invalid day given (Case sensitive test)
    with pytest.raises(ValueError):
        requiredData = filterData(fuelData, parameters={'Day':'Today'})

    #Invalid Fueltype test
    with pytest.raises(KeyError):
        filterData(fuelData, parameters={'FuelType':'Electric'})

    #requiredData = filterData(fuelData, parameters={'Suburb':'Perth'})
    #requiredData = filterData(fuelData, parameters={'FuelType':'Diesel','Day':'yesterday'})