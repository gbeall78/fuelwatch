from fuelData import FuelTypes
from airium import Airium

def fuelTable(data):
    html = Airium()

    with html.table():
        ft = "Fuel type: " + FuelTypes[data[0]["fuelType"]]
        with html.div(klass='fueltype_header', _t=ft):
            with html.tr():
                html.th(klass='Price', _t='Price')
                html.th(klass='Name', _t='Name')
                html.th(_t='Address')
                html.th(klass='Location', _t='Location')
            for d in data:
                with html.tr():
                    html.td(_t=d['price'])
                    html.td(_t=d['trading-name'])
                    html.td(_t=d['address'])
                    html.td(_t=d['location'])

    return str(html)
