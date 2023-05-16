import requests
import re

def geocode(address):
    # this gets the longitude and latitude of the address
    try:
        params = { 'format'        :'json',
                   'addressdetails': 1,
                   'q'             : address}
        headers = { 'user-agent'   : 'TDI' }   #  Need to supply a user agent other than the default provided
                                               #  by requests for the API to accept the query.
        return requests.get('http://nominatim.openstreetmap.org/search',
                            params=params, headers=headers)
    except:
        return 'no'

def get_address_lat_long(address):
    # given a street address, this finds the latitude and longitude
       
    address_response = geocode(address)
    if address_response != 'no':
        address_data = address_response.json()
        if len(address_data) > 0:
            lat = address_data[0]['lat']
            lon = address_data[0]['lon']
            return lat,lon
    return 'no', 'no'