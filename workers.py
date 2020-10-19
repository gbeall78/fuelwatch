import exceptions
from validate import validateHTMLStyleAttribute,validateHTMLClassAttribute
from feedparser import parse
from pprint import pprint
from geocoder import ip

def getPrices(product_id='1', suburb='', day='today', brand='', surrounding=''):
    options = 'Product=' + product_id
    options += '&Day=' + day
    if suburb != '':
        options += '&Suburb=' + suburb
    return parse('https://www.fuelwatch.wa.gov.au/fuelwatch/fuelWatchRSS?' + options)

def userLocation():
     return ip('me')

def tabs(number):
    tabs = str()
    for n in range(number):
        tabs += '\t'
    return tabs

def buildTableRow(data):
    rows = str()
    for d in data:
        rows += f'{tabs(4)}<tr>\n'
        rows += f'{tabs(5)}<td>{d["price"]}</td>\n'
        rows += f'{tabs(5)}<td>{d["trading-name"]}</td>\n'
        rows += f'{tabs(5)}<td>{d["address"]}</td>\n'
        rows += f'{tabs(5)}<td>{d["location"]}</td>\n'
        rows += f'{tabs(4)}</tr>\n'
    return rows

def buildTable(header, data, style='', className=''):

    try:
        if style != '':
            validateHTMLStyleAttribute(style)
        if className != '':    
            validateHTMLClassAttribute(className)
    except exceptions.invalidStyleParameter as err:
        pprint(err)
    except exceptions.invalidClassParameter as err:
        pprint(err)
    else:
        table = str()
        table += f'{tabs(3)}<table'
        
        if style != '':
            table += f' {style}"'
        
        if className != '':
            table += f' {className}"'
        
        table += f'>\n'
            
        table += f'{tabs(4)}<tr>\n' 
        for h in header:
            table += f'{tabs(5)}<th>{h}</th>\n'
        table += f'{tabs(4)}</tr>\n'
        table += buildTableRow(data)
        table += f'{tabs(3)}</table>\n'
        return table
