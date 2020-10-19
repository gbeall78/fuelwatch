import exceptions
from pprint import pprint
from workers import getPrices, userLocation, buildTable

def buildTableTest():
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

    try: #Test basic functionality
        #Weird style
        #buildTable(testDataHeader, testDataServo, style="test:test:test")

        #missing ;
        #buildTable(testDataHeader, testDataServo, style="test:test; test2:test2")
        #buildTable(testDataHeader, testDataServo, style="test:test test2:test2")
        #buildTable(testDataHeader, testDataServo, style="test:test")
        
        #Valid style
        #buildTable(testDataHeader, testDataServo, style="test:test;")

        #Bad class name
        #buildTable(testDataHeader, testDataServo, style="test:test;", className="34")
        #buildTable(testDataHeader, testDataServo, style="test:test;", className="w-ord")
        
        #valid class name
        buildTable(testDataHeader, testDataServo, style="test:test;", className="_word")
        buildTable(testDataHeader, testDataServo, style="test:test;", className="word")
    except exceptions.invalidStyleParameter:
        pprint('Invalid style parameter given.')
    except exceptions.invalidClassParameter:
        pprint('Invalid class parameter given.')
    except:
        pprint("Invalid function usage.")
    else:
        try: #Test Data header validity
            
            #Too few items
            buildTable([], testDataServo)
            #Too many items
            buildTable([], testDataServo)
        except exceptions.noTableHeaderException:
            pprint("Table header was blank")
        except exceptions.tableHeaderDataSizeMismatchException:
            pprint("Table header had a different number of columns to the provided data")
        except:
            pprint("Invalid table header usage")
        else:
            try: #Test data validity


                buildTable(testDataHeader, testDataServo)
                buildTable(testDataHeader, testDataServo)
                buildTable(testDataHeader, testDataServo)
                buildTable(testDataHeader, testDataServo)
                buildTable(testDataHeader, testDataServo)
            except exceptions.invalidDataException:
                pprint('Invalid data.')
            except:
                pprint('Invalid data.')
            else:
                pprint('All Tests passed! Have a cookie!')



def runTest():
    #pprint(getPrices())
    #pprint(userLocation().city)
    buildTableTest()    

runTest()