# import altair as alt
import plotly.express as px
import numpy as np
from numpy import pi, sin, cos
import plotly.graph_objs as geocode 
import requests
import re


def geocode(address):
    # this gets the longitude and latitude of the address

    params = { 'format'        :'json',
               'addressdetails': 1,
               'q'             : address}
    headers = { 'user-agent'   : 'TDI' }   #  Need to supply a user agent other than the default provided
                                           #  by requests for the API to accept the query.
    return requests.get('http://nominatim.openstreetmap.org/search',
                        params=params, headers=headers)


def get_address_lat_long(address):
    # given a street address, this finds the latitude and longitude
       
    address_response = geocode(address)
    address_data = address_response.json()
    lat = address_data[0]['lat']
    lon = address_data[0]['lon']
    return lat,lon

def plot_freeebikes(bike_df, addy, R, color_pallet):#, addy, max_dist):
    lat_add, lon_add = get_address_lat_long(addy)
    fig = (px.scatter_mapbox(bike_df, lat="lat", lon="lon", zoom=9.7, color='plot_bikes',
                            color_discrete_map=color_pallet,#{ 'no bikes':'#92B6B1', 'bike available':'#0E6BA8',
                                                #'ebike and bike available':'#0A2472', 'free ebike':'#BF1A2F'},
                            category_orders={'plot_bikes':['No bikes',
                                                 'Bike(s)', 'Ebike(s) and bike(s)','Free ebike(s)']},
                             width=550,
                            height=500,
                            hover_name="name", hover_data={"lon":False,"lat":False,"plot_bikes":False, "bikes_available":True, 
                            "ebikes_available":True}
          ))

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                     mapbox={'center': {'lon': float(lon_add), 'lat': float(lat_add)},
                            'zoom':15})
    fig.update_layout(legend=dict(font=dict(size= 14)))
#     R = 0.005
    center_lon = float(lon_add)
    center_lat = float(lat_add)
    t = np.linspace(0, 2*pi, 100)
    circle_lon =center_lon + R*cos(t)
    circle_lat =center_lat +  R*sin(t)/ (center_lat /(111*cos(center_lon * 2 * pi /360)))
   
    coords=[]
    for lo, la in zip(list(circle_lon), list(circle_lat)):
        coords.append([lo, la])

    layers=[{'sourcetype': 'geojson',
             'source':{ "type": "Feature",
                     "geometry": {"type": "LineString",
                                  "coordinates": coords
                                  }
                    },
             'color': '#00ABE7',
             'type' : 'line',
             'line':{'width':3}
            }]
   
   
    fig.update_layout(
    mapbox={'layers':layers,
        'zoom':13.5}, legend_title="",)
    fig.update_traces(
    marker=dict(
        size=15),
    selector=dict(mode="markers"),
)

# fig.update_layout(
#     title="Performance Results",
#     legend_title="",
#     ...,
# )

    return fig
