import altair as alt
import plotly.express as px


def plot_current_freeebikes(bike_df, color_pallet):
    fig = (px.scatter_mapbox(bike_df, lat="lat", lon="lon", zoom=9.8, color='plot_bikes',
                            color_discrete_map=color_pallet,#{ 'no bikes':'#92B6B1', 'bike available':'#0E6BA8',
                                                # 'ebike and bike available':'#0A2472', 'free ebike':'#BF1A2F'},
                            # color_discrete_map={ 'no bikes':'#C8C2AE', 'bike available':'#1E91D6',
                            #                     'ebike and bike available':'#0000FF', 'free ebike':'#D62828'},
                            category_orders={'plot_bikes':['No bikes',
                                                 'Bike(s)', 'Ebike(s) and bike(s)','Free ebike(s)']},
                             width=550,
                            height=500,
                            hover_name="name", hover_data={"lon":False,"lat":False,"plot_bikes":False, "bikes_available":True, 
                            "ebikes_available":True}
          ))

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, legend_title="",mapbox={'center': {'lon': -73.98, 'lat': 40.76},
                            'zoom':10})
    fig.update_layout(legend=dict(font=dict(size= 14)))
    return fig
