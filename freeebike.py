import requests
import re
import pandas as pd
import numpy as np
from numpy import pi, sin, cos
from datetime import datetime, timedelta
import dill
# import matplotlib

def temperature_at_address(address):
    # this will return a list with the temperature, rain, snow, windspeed, where the temperature is an integer in 
    # farenheight, the rain is a 1 or 0, the snow is a 1 or 0 and the windspeed is an integer in mph
    pass_back = []
    temp_response = requests.get(address)
    temp_data=temp_response.json()
    pass_back.append(int(temp_data['data']['temperature'][0]))
    weather_sentence = temp_data['data']['weather'][0]
    if 'Showers' in weather_sentence and 'Chance' not in weather_sentence:
        pass_back.append(1)
    elif 'Rain' in weather_sentence and 'Chance' not in weather_sentence:
        pass_back.append(1)
    elif 'Drizzle' in weather_sentence and 'Chance' not in weather_sentence:
        pass_back.append(1)
    else:
        pass_back.append(0)
    if 'Snow' in weather_sentence and 'Chance' not in weather_sentence:
        pass_back.append(1)
    else:
        pass_back.append(0)        
    wind_sentence = temp_data['data']['text'][0]
    reg_wind = r'wind ([0-9]*) to ([0-9]+)|wind around ([0-9]*)'
    m = re.findall(reg_wind, wind_sentence)
    windspeed_list = []
    for i in m[0]:
        if i != '':
            windspeed_list.append(int(i))
    wind = sum(windspeed_list)/len(windspeed_list)
    pass_back.append(wind)
    return pass_back

def add_dist_column(df_citibike_live_stations, lon, lat):
    df_citibike_live_stations['dist']= (((df_citibike_live_stations['lat'] - float(lat))*(float(lat) /(111*cos(float(lon) * 2 * pi /360))))**2+(df_citibike_live_stations['lon'] - float(lon))**2)**(1/2)
    return df_citibike_live_stations

def get_close_stations(df_citibike_live_stations, max_dist):
    # Get the stations close enough to your location
    good_stations = df_citibike_live_stations[['name','dist', 'terminal','free_ebikes', 'bikes_available', 'docks_available', 'ebikes_available', 'bike_angels_action', 'bike_angels_points'] ].loc[df_citibike_live_stations['dist'] <= max_dist]
    return good_stations

def add_weather_data(X, ttemp, sent, rain, snow):
    X['temp'] = ttemp
    X['wind'] = sent
    X['rain'] = rain
    X['snow'] = snow
    return X

def add_time_data(good_stations):
    good_stations['hour'] = datetime.now().hour
    good_stations['day_of_week'] = datetime.now().weekday()
    return good_stations

def make_predictions_df(good_stations):
    for n in range(10,70,10):
        name = 'model_'+str(n)+'.pkd'
        col_name = str(n)+' min'
        with open(name, "rb") as f:
            model = dill.load(f)
            pre = model.predict_proba(good_stations)
        col = []
        for station in pre:
            col.append(int(station[1]*100))
        good_stations[col_name] = col
    predictions = good_stations.copy()[['name', 'dist','ebikes_available', '10 min', '20 min', '30 min', '40 min', '50 min', '60 min']]
    predictions = predictions.rename(columns={"name": "stations", "ebikes_available": "ebikes"})
    predictions = predictions.sort_values('dist',axis=0, ascending=True)
    predictions['dist'] = round(predictions['dist']*271819.44)
    predictions = predictions.rename(columns={"dist": "dist (ft)"})

    # predictions = predictions.drop(['dist'], axis=1)
    predictions = predictions.set_index('stations')
    return predictions

# def rain_condition(v):
#     if v > 85:
#         return 'Go for it!'
#     elif v > 75:
#         return 'Likely'
#     elif v > 50:
#         return 'Maybe?'
#     return 'Nah'

# def make_pretty(styler):
#     styler.format(rain_condition)
#     # styler.background_gradient(axis=None, vmin=20, vmax=100, cmap="YlGnBu")
#     return styler


def percent(re, thresh_1, thresh_2, thresh_3):
    col = ['10 min', '20 min', '30 min', '40 min', '50 min', '60 min']
    re[col] = np.where(re[col] > thresh_1, -6, re[col])
    re[col] = np.where(re[col] > thresh_2, -5, re[col])
    re[col] = np.where(re[col] > thresh_3, -4, re[col])
    re[col] = np.where(re[col] > 0, 0, re[col])
    for c in col:
        re[c] = re[c].map({-6:'Good!', -5:'Likely', -4:'Maybe?', 0:'Nah...'})

    return re

def red_background_zero_values(cell_value):
    highlight_0 = 'background-color: #00abe7;' #d33f49;'
    highlight_1 = 'background-color: #4ab0cc;' #e26d3d;' #b87174;'
    highlight_2 = 'background-color: #85b3b6;' #ed9234;' #97aca8;'
    highlight_3 = 'background-color: #b1b6a6;' #f6ae2d;' #92b6b1;'
    default = ''
    if cell_value == 'Good!':
        return highlight_0
    elif cell_value == 'Likely':
        return highlight_1
    elif cell_value == 'Maybe?':
        return highlight_2
    elif cell_value == 'Nah...':
        return highlight_3
    else:
        return default

def combine_all(lat, lon, max_dist, df_citibike_live_stations, thresh_1 = 85, thresh_2 = 70, thresh_3 =50):
    search_address = 'http://forecast.weather.gov/MapClick.php?lat='+str(lat)+'&lon='+str(lon)+'&FcstType=json'
    ttemp, rain, snow, sent = temperature_at_address(search_address)
    df_citibike_live_stations = add_dist_column(df_citibike_live_stations, lon, lat)
    good_stations = get_close_stations(df_citibike_live_stations, max_dist)
    if sum(good_stations.free_ebikes) == 0:
        return 'There are no freeebikes in this range.'
    good_stations = good_stations[good_stations['free_ebikes']==1]
    good_stations = add_time_data(good_stations)
    good_stations = add_weather_data(good_stations, ttemp, sent, rain, snow)
    predictions = make_predictions_df(good_stations)
    # dfpredictions = predictions.astype({'ebikes':'int'})
    # predictions = predictions.set_index(['ebikes'],append=True, drop=True)
    # pre = predictions.loc[:].style.pipe(make_pretty)
    # pre = pre.reset_index(level='ebikes')
    pre = percent(predictions, thresh_1, thresh_2, thresh_3)
#     red = red_background_zero_values(pre)
#     pre = predictions.loc[:].style.pipe(make_pretty)
# #     pre = pre.reset_index(level='ebikes')

    pre = pre.style.applymap(red_background_zero_values)
    pre = pre.format({'ebikes': "{:4g}", 'dist (ft)': "{:4g}"})
    return pre


    
# max_dist = 0.01    
# predictions = combine_all(lat_add, lon_add, max_dist, data)
# predictions

# lat = 40.673648
# lon = -73.971529
# max_dist = .0200
# thresh_1 = 70
# thresh_2 = 50
# thresh_3 = 30
# combine_all(lat, lon, max_dist, df_citibike_live_stations, thresh_1, thresh_2, thresh_3)
