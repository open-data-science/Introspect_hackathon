import sys
import json

import numpy as np
import pandas as pd


def get_username_from_dump(users_json, user_id):
    """ Get username from dump file by user id.
    
    Args:
        users_json: dict object with dump data
        user_id: id to find
    """
    for user in users_json:
        if user.get('id', '') == user_id:
            return user.get('name', '')
    return ''


def filter_coordinate(data_row, coordinate_field):
    """ Get correct coordinates from dataframe row.
    Filter data by 'geolocation_type' field.
    
    Args:
        data_row: data
        coordinate_field: coordinate field name
    """
    correct_location_types = [
        'city', # OSM
        'locality', # yandex
        'province', # yandex
        'area' # yandex
    ]
    
    if data_row['geolocation_type'] in correct_location_types:
        return np.float(data_row[coordinate_field])
    else:
        return None


def prepare_user_data(settings_filepath):
    """ Prepare user geodata csv file.
    Connect geodata from geolocator service with usernames and filer correct coordinates.
    
    Args:
        settings_filepath: path to settings file
    """
    print('open settings: {}'.format(settings_filepath))
    with open(settings_filepath, 'r') as settings_file:
        settings = json.load(settings_file)
    
    with open(settings['users_dump_file'], 'r') as users_json_file:
        users_json = json.load(users_json_file)
    
    user_locations = pd.read_csv(settings['users_locations_file'])
    
    user_locations['user'] = user_locations['id'].apply(lambda x: get_username_from_dump(users_json, x))
    user_locations['latitude'] = user_locations.apply(lambda x: filter_coordinate(x, 'geolocation_lat'), axis=1)
    user_locations['longitude'] = user_locations.apply(lambda x: filter_coordinate(x, 'geolocation_lon'), axis=1)
    
    user_locations.to_csv(settings['output_file'], index=False)
    

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        prepare_user_data(sys.argv[1])
    else:
        print('settings file needed')