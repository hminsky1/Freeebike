import streamlit as st
import plotly.express as px

from live_citi_data import make_citi_df
from bike_plotter import plot_current_freeebikes
from freeebike import combine_all
from zoom_bike_plotter import plot_freeebikes
from address_to_lon_lat import get_address_lat_long

from PIL import Image


def app():
    im = Image.open('citi_icon.png')
    st.set_page_config(layout="wide", page_title="Freeebike", page_icon = im)
    hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
    st.markdown(hide_default_format, unsafe_allow_html=True)
    st.title("Freeebike")
    st.markdown("See all the free electric bikes in the city or enter an address in Brooklyn to see the probability of a nearby electric bike remaining free in the future.")
    plot_colors={ 'No bikes':'#B1B6A6', 'Bike(s)':'#696773',
                  'Ebike(s) and bike(s)':'#363946', 'Free ebike(s)':'#00ABE7'}
    # plot_colors={ 'No bikes':'#BDD4E7', 'Bike(s)':'#40798C',
    #               'Ebike(s) and bike(s)':'#0A1045', 'Free ebike(s)':'#219A45'}
    # plot_colors={ 'No bikes':'#92B6B1', 'Bike(s)':'#0E6BA8',
    #               'Ebike(s) and bike(s)':'#0A2472', 'Free ebike(s)':'#D33F49'}
    left, right = st.columns(2)
    with right:
        addy = st.text_input('Address')#, value = '1902 8th Ave, Brooklyn')
        max_dist_ft = st.slider('Distance (in feet)', min_value = 500, max_value = 2500,
	    				 value = 1500, step = 250, format='%i')
        max_dist = max_dist_ft/271819.44
        # thresh_1 = 60
        # thresh_2 = 40
        # thresh_3 = 20
        ch=0
        thresh_1 = 85 #st.number_input("Good! threshold", 0, 100, value=85, step=1)
        thresh_2 = 70 # st.number_input("Likely threshold", 0, 100, value=70, step=1)
        thresh_3 = 50 # st.number_input("Maybe? threshold", 0, 100, value=50, step=1)
        # if thresh_1 > thresh_2 and thresh_2 > thresh_3:
        if addy:
            if 'brooklyn' in addy.lower():#if addy:
            # ch = 0
            # try:
                lat_add, lon_add = get_address_lat_long(addy)
                if lat_add == 'no':
                    st.write('Make sure you don\'t have any typos')
                else:
                # st.write(lat_add)
                    data = make_citi_df()
                    st.write(combine_all(lat_add, lon_add, max_dist, data, thresh_1, thresh_2, thresh_3))
                #    if 'brooklyn' in addy.lower():
                    st.write('Good! - better than 85\% chance or remaining a freebike.')
                    st.write('Likely - 70 to 85\% chance or remaining a freebike.')
                    st.write('Maybe? - 50 to 70\% chance or remaining a freebike.')
                    st.write('Nah... - at best a 50\% chance or remaining a freebike.')

                    ch = 1
        # except:
            # st.write('Make sure you don\'t have any typos')
            else:#    except:
                st.write('Try another address. Make sure it is in Brooklyn.')
        # else:
        #     st.write('Make sure "Go for it!" is higher than "Likely" which is higher than "Mayby".')
    with left:
        if addy and ch == 1:
            st.write(plot_freeebikes(data, addy, max_dist, plot_colors))
        else:
            data = make_citi_df()
            st.write(plot_current_freeebikes(data, plot_colors))  	
    # st.markdown("This app was made by Helen Minsky because I love riding Citibikes. It is my capstone project for the data incubator. If you have questions about this app or just want to discuss bikeshare programs, you can contact me at helen.keays.minsky@mg.thedataincubator.com.")
    st.markdown('Made by Helen Minsky | helen.keays.minsky@mg.thedataincubator.com')
    st.markdown('The model was last updated on May 24, 2023')

if __name__ == '__main__':
    app()