import exceptions
from pprint import pprint
import workers
import htmlBuilder
from flask import Flask

app = Flask(__name__)

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
        #htmlBuilder.buildTable(testDataHeader, testDataServo, style="test:test:test")

        #missing ;
        #htmlBuilder.buildTable(testDataHeader, testDataServo, style="test:test; test2:test2")
        #htmlBuilder.buildTable(testDataHeader, testDataServo, style="test:test test2:test2")
        #htmlBuilder.buildTable(testDataHeader, testDataServo, style="test:test")
        
        #Valid style
        #htmlBuilder.buildTable(testDataHeader, testDataServo, style="test:test;")

        #Bad class name
        #htmlBuilder.buildTable(testDataHeader, testDataServo, style="test:test;", className="34")
        #htmlBuilder.buildTable(testDataHeader, testDataServo, style="test:test;", className="w-ord")
        
        #valid class name
        htmlBuilder.buildTable(testDataHeader, testDataServo, style="test:test;", className="_word")
        htmlBuilder.buildTable(testDataHeader, testDataServo, style="test:test;", className="word")
    except exceptions.invalidStyleParameter:
        pprint('Invalid style parameter given.')
    except exceptions.invalidClassParameter:
        pprint('Invalid class parameter given.')
    except:
        pprint("Invalid function usage.")
    else:
        try: #Test Data header validity
            
            #Too few items
            htmlBuilder.buildTable([], testDataServo)
            #Too many items
            htmlBuilder.buildTable([], testDataServo)
        except exceptions.noTableHeaderException:
            pprint("Table header was blank")
        except exceptions.tableHeaderDataSizeMismatchException:
            pprint("Table header had a different number of columns to the provided data")
        except:
            pprint("Invalid table header usage")
        else:
            try: #Test data validity


                htmlBuilder.buildTable(testDataHeader, testDataServo)
                htmlBuilder.buildTable(testDataHeader, testDataServo)
                htmlBuilder.buildTable(testDataHeader, testDataServo)
                htmlBuilder.buildTable(testDataHeader, testDataServo)
                htmlBuilder.buildTable(testDataHeader, testDataServo)
            except exceptions.invalidDataException:
                pprint('Invalid data.')
            except:
                pprint('Invalid data.')
            else:
                pprint('All Tests passed! Have a cookie!')

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
    
    strFT = f'Fuel type: {workers.FuelTypes[requiredData[0]["fuelType"]]}\n{htmlBuilder.buildTable(["Price","Name","Address","Location"],requiredData)}'
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
