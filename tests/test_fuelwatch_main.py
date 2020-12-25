import workers

def test_getFuelData():
    fuelData = list()
    fuelData = workers.getFuelData()

    daysCollected = len(fuelData)
    if(daysCollected == 3):
        pprint("Yesterdays, todays and tomorrows data has been collected.")
    elif(daysCollected == 2 and not workers.tomorrowReleased()):
        pprint("Before 2:30PM. Yesterdays and todays data have been collected.")
