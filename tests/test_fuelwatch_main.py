import pytest
from fuelData import FuelData

def test_filterData():
    with pytest.raises(AttributeError):
        today = FuelData()

    today = FuelData('today')
    
    #Test too many stations requested
    count = len(today.data[0]['stations']) 
    assert len(today.filterData(parameters={'Count':600})) == count

    #Invalid Fueltype test
    with pytest.raises(KeyError, match=r"^Invalid fuel type given. Valid options are:.*$"):
        today.filterData(parameters={'FuelType':'Electric'})