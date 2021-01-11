import exceptions as e
import pytest
from htmlBuilder import buildTable
from validate import validateHTMLStyleAttribute,validateHTMLClassAttribute

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
    with pytest.raises(e.invalidStyleParameter):
        validateHTMLStyleAttribute("test:test:test")

    #missing ;
    '''
    with pytest.raises(e.invalidStyleParameter):
        buildTable(testDataHeader, testDataServo, style="test:test")
    with pytest.raises(e.invalidStyleParameter):
        buildTable(testDataHeader, testDataServo, style="test:test; test2:test2")
    with pytest.raises(e.invalidStyleParameter):
        buildTable(testDataHeader, testDataServo, style="test:test test2:test2")
    
    #Valid style
    buildTable(testDataHeader, testDataServo, style="test:test;")

    #Bad class name
    with pytest.raises(e.invalidClassParameter):
        buildTable(testDataHeader, testDataServo, style="test:test;", className="34")
    with pytest.raises(e.invalidClassParameter):
        buildTable(testDataHeader, testDataServo, style="test:test;", className="w-ord")
        
    #valid class name
    buildTable(testDataHeader, testDataServo, style="test:test;", className="_word")
    buildTable(testDataHeader, testDataServo, style="test:test;", className="word")

    #Too few items
    with pytest.raises(e.noTableHeaderException):
        buildTable([], testDataServo)

    #Too many items
    with pytest.raises(e.tableHeaderDataSizeMismatchException):
        buildTable(testDataHeader+testDataHeader, testDataServo)
'''            