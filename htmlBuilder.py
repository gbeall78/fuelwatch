import exceptions
from validate import validateHTMLStyleAttribute,validateHTMLClassAttribute
from flask import url_for
from workers import FuelTypes

def tabs(number):
    return '\t' * number

def header():
    header = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Fuel Watch</title>

            <link rel="stylesheet" href="{url_for('static',filename='styles/fuelwatch_default.css')}">
        </head>
        <body>
    '''
    return header

def footer():
    footer = f'''
        </body>
    </html>    
    '''
    return footer

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
            table += f'{tabs(5)}<th class="{h}">{h}</th>\n'
        table += f'{tabs(4)}</tr>\n'
        table += buildTableRow(data)
        table += f'{tabs(3)}</table>\n'
        return table

def fuelTable(data):
    return f'''
    <div class="fueltype_header">Fuel type: {FuelTypes[data[0]["fuelType"]]}</div>
    {buildTable(["Price","Name","Address","Location"],data)}
    '''
