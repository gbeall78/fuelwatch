import feedparser


def get_fuel(product_id):
    data = feedparser.parse('http://www.fuelwatch.wa.gov.au/fuelwatch/fuelWatchRSS?Product='+str(product_id)+'&Suburb=Cloverdale')
    return data['entries']
  
unleaded = 1
premium_unleaded = 2

u_prices = get_fuel(unleaded)
pu_prices = get_fuel(premium_unleaded)

print(u_prices)