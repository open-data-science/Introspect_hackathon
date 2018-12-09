import pandas as pd

import folium
from folium import plugins
from folium import IFrame

import json
import time

import matplotlib.pyplot as plt
from plotly import tools
import plotly.graph_objs as go
import plotly
import pandas as pd
from plotly.offline import plot

from geopy.geocoders import Nominatim
import configparser

config = configparser.ConfigParser()
config.read('settings.ini')
username = config['PLOTLY']['username']
api_key = config['PLOTLY']['api_key']

plotly.tools.set_credentials_file(username=username, api_key=api_key)
geolocator = Nominatim(user_agent='artgor')


def plot_top_channels(plot_type='matplotlib', top_n=20):
    """
    Plot top channels by user count.
    
    Use channels.json to get channels and user count in them.
    Can plot either top N channels in matplotlib or in Plotly
    
    :params: plot_type - matplotlib/plotly
    :params: top_n - plot top n channels. If None - plot all
    """
    # load file
    with open('shared/latest_dump/channels.json', 'r') as f:
        channels = json.load(f)
    
    # number of users in channels
    d = {i['name']: len(i['members']) for i in channels}
    
    # sort data and convert to pandas DF. set channel as index for plotting
    sorted_d = sorted(d.items(), key = lambda x: x[1], reverse=True)
    df = pd.DataFrame(sorted_d, columns=['channel', 'user_count'])
    df = df.set_index('channel')
    
    if top_n is None:
        top_n = len(df)
    
    if plot_type == 'matplotlib':
        df[:top_n].sort_values('user_count').plot(kind='barh', figsize=(12, 8));
        plt.title(f'Топ-{top_n} каналов по количеству пользователей');
        plt.show()
        
    elif plot_type == 'plotly':
        data = [go.Bar(
                x=df[:top_n].index,
                y=df[:top_n]['user_count'],
                name='user counts'
            )]
        layout = go.Layout()
        fig = go.Figure(data=data, layout=layout)
        plot(fig, filename='top_channels.html')
    else:
        raise ValueError('Possible values: matplotlib or plotly')
        
def prepare_data_for_folium(return_df=False, save_df=True, df_name='user_geo'):
    """
    Prepairs data for foluim in a naive way.
    
    Uses information about user time zone to prepare data for using in folium.
    
    :params: return_df - whether to return df
    :params: save_df - whether to save df
    :params: df_name - name of saved df
    """
    with open('shared/latest_dump/users.json', 'r') as f:
        users = json.load(f)
    
    # mapping of users to timezone
    user_tz = {i['name'] : i['tz'] if 'tz' in i.keys() else '' for i in users}
    
    # unique tz
    tzs = list(set(list(user_tz.values())))
    
    #cities
    city_list = sorted([i.split('/')[1] for i in tzs[1:]])
    
    # getting data from api. There is a limit of number of requests
    # so sleep is used
    city_geo = {}
    for i, c in enumerate(city_list):
        if i % 30 == 0:
            time.sleep(1)
        
        location = geolocator.geocode(c)
        city_geo[c] = (location.latitude, location.longitude)
        
    # create DataFrame
    u_c_df = pd.DataFrame.from_dict(user_tz, orient='index')
    u_c_df.reset_index(inplace=True)
    u_c_df.columns = ['user', 'tz']
    
    u_c_df['city'] = u_c_df['tz'].apply(lambda x: x.split('/')[1] if '/' in x else '')
    
    # dropping empty rows
    u_c_df = u_c_df.loc[u_c_df['city'] != '']
    u_c_df['latitude'] = u_c_df['city'].apply(lambda x: city_geo[x][0])
    u_c_df['longitude'] = u_c_df['city'].apply(lambda x: city_geo[x][1])
    u_c_df['user_count'] = u_c_df.groupby('city')['user'].transform('count')
    
    if save_df:
        u_c_df.to_csv(f'{df_name}.csv', index=False)
        
    if return_df:
        return df
    
def make_plotly_map(u_c_df, plot_by='city', add_heatmap=True):
    """
    Make folium map.
    
    Makes folium map with heatmap.
    Can be done by cities or geo data.
    Text of markers is made with html, so it can be easily changed to show any information.
    
    :params: u_c_df  pandas DataFrame with data. Must have columns: user (display name), city,
            latitude, longtitude. 
    :params: plot_by - It is adequate to do it by city, but there is a case,
            when it was better to do it by geo - when data isn't completely clean.
            add_heatmap - whether to add heatmap.
    
    """
    m = folium.Map([], zoom_start=15)
    if add_heatmap:
        geo_matrix = u_c_df[['latitude', 'longitude']].values
        m.add_child(plugins.HeatMap(geo_matrix, radius=10, min_opacity=0.6, max_zoom=10, max_val=1, blur=10, gradient={0.4: 'blue', 0.65: 'lime', 1: 'crimson'}));
    
    marker_cluster = plugins.MarkerCluster().add_to(m)
    
    if plot_by == 'city':
        main_col = 'city'
        count_col = 'user_count_city'
        
    elif plot_by == 'geo':
        main_col = 'latitude'
        count_col = 'user_count_lat'
    else:
        raise ValueError('Possible values: city or geo')
    
    for c in u_c_df[main_col].unique():
        # make list of first 5 people
        city_users = list(u_c_df.loc[u_c_df[main_col] == c, 'user'].values)[:5]
        #city_users = '\n'.join(city_users)
        
        # user count
        user_count = u_c_df.loc[u_c_df[main_col] == c, count_col].unique()[0]
        
        # city name
        city_name = c if main_col == 'city' else u_c_df.loc[u_c_df[main_col] == c, 'city'].unique()[0]
        
        # creating folium markers
        html=f"""
            <h2> Город: {city_name}</h2><br>
            Количество пользователей: {user_count}<br>
            Здесь живут такие люди:<br>
            """
        for u in city_users:
            html += u + '<br>'
        
        iframe = IFrame(html=html, width=500, height=300)
        popup = folium.Popup(iframe, max_width=300)
        
        folium.Marker(location=[u_c_df.loc[u_c_df[main_col] == c, 'latitude'].unique()[0],
                                u_c_df.loc[u_c_df[main_col] == c, 'longitude'].unique()[0]],
                            popup=popup
                           ).add_to(marker_cluster)
        
    return m