import feedparser
import workers
from pprint import pprint

Day = ['yesterday'] #, 'today', 'tomorrow']

FuelTypes = {
    '1' : 'Unleaded Petrol',
}
'''
    '2' : 'Premium Unleaded',
    '4' : 'Diesel',
    '5' : 'LPG',
    '6' : '98 RON',
    '10' : 'E85',
    '11' : 'Brand diesel',
}
'''

    
scrapedData = list()

for d in Day:
    dList = list()
    for ft in FuelTypes:
        scrape = workers.getPrices(day=d,product_id=ft, suburb='Nollamara')
        print(type(scrape))
        fList = list()
        s=sorted(scrape['items'], key=lambda item : item['price'], reverse=True)

        for i in s:
            servo = dict()
            servo = {
                'price' : i['price'],
                'brand' : i['brand'],
                'trading-name' : i['trading-name'],
                'location' : i['location'],
                'address' : i['address'],
                'longitude' : i['longitude'],
                'latitude' : i['latitude'],
            }
            
            fList.append(servo)
        dList.append(fList)
    scrapedData.append(dList)

#requiredData = filter(scrapedData)

pprint(workers.buildTableRow(scrapedData[0][0]))