import requests
import pandas as pd
import numpy as np
# import altair as alt


def get_live_citi_data():
    # pull live citibike data as json file
    URL = "https://layer.bicyclesharing.net/map/v1/nyc/stations"
    r = requests.get(url = URL)
    current_station = r.json()['features']
    return current_station

def get_live_citibike_data(current_station):
    # turn json file of current citibike data into a dataframe
    citibike_live_df_orig = pd.DataFrame.from_dict(current_station)
    df_geometry = citibike_live_df_orig['geometry'].apply(pd.Series)
    df_properties = citibike_live_df_orig['properties'].apply(pd.Series)
    df_properties = df_properties.merge(df_geometry, how='inner', left_index=True, right_index=True)
    df_citibike_live_stations = df_properties[['station_id', 'name', 'terminal', 'capacity', 'bikes_available', 'docks_available', 'bikes_disabled', 
            'docks_disabled', 'ebikes_available', 'bike_angels_action','bike_angels_points', 'coordinates']]
    return df_citibike_live_stations

def plot_bike_colors(row):
    if row.free_ebikes == 1:
        return 'Free ebike(s)'
    elif row.ebikes_available > 0:
        return 'Ebike(s) and bike(s)'
    elif row.bikes_available > 0:
        return 'Bike(s)'
    else:
        return 'No bikes'
        
def prepare_live_citibike_data(df_citibike_live_stations):
    # clean up dataframe and make required columns
    split = pd.DataFrame(df_citibike_live_stations['coordinates'].to_list(), columns = ['lon', 'lat'])
    df_citibike_live_stations = pd.concat([df_citibike_live_stations, split], axis=1)
    df_citibike_live_stations['ebikes_available'] = df_citibike_live_stations['ebikes_available'].fillna(0)
    df_citibike_live_stations['bike_angels_action'] = df_citibike_live_stations['bike_angels_action'].fillna('neutral')
    df_citibike_live_stations['bike_angels_points'] = df_citibike_live_stations['ebikes_available'].fillna(0)
    df_citibike_live_stations['free_ebikes'] = np.where((df_citibike_live_stations['ebikes_available']>0) & (df_citibike_live_stations['bikes_available']==df_citibike_live_stations['ebikes_available'] ), 1, 0)     
    df_citibike_live_stations['plot_bikes'] =  df_citibike_live_stations.apply(lambda row: plot_bike_colors(row), axis=1)
    return df_citibike_live_stations

def make_citi_df():#(current_station):
#     get all data on current citibikes in the form of a dataframe
    current_station = get_live_citi_data()
    df_citibike_live_stations = get_live_citibike_data(current_station)
    df_citibike_live_stations = prepare_live_citibike_data(df_citibike_live_stations)
    return df_citibike_live_stations
    
# bike_df = make_citi_df()