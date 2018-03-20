# -*- coding: utf-8 -*-

import os, logging
import json
from pprint import pprint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Table, Column, Integer, String, Boolean, DateTime, MetaData, ForeignKey
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

Base = declarative_base()

class UserData(Base):
    __tablename__ = 'imported_user_data'

    id = Column('id', String, primary_key=True)
    name = Column('name', String)
    deleted = Column('deleted', Boolean)

    tz = Column('tz', String)
    tz_label = Column('tz_label', String)
    tz_offset = Column('tz_offset', Integer)
    is_admin = Column('is_admin', Boolean)
    is_owner = Column('is_owner', Boolean)
    is_primary_owner = Column('is_primary_owner', Boolean)
    is_restricted = Column('is_restricted', Boolean)
    is_ultra_restricted = Column('is_ultra_restricted', Boolean)
    is_bot = Column('is_bot', Boolean)
    updated = Column('updated', Integer)
    is_app_user = Column('is_app_user', Boolean)

    title = Column('title', String)                               
    phone = Column('phone', String)                               
    skype = Column('skype', String)                               
    real_name = Column('real_name', String)                               
    real_name_normalized = Column('real_name_normalized', String)                               
    display_name = Column('display_name', String)                               
    display_name_normalized = Column('display_name_normalized', String)                               
    fields = Column('fields', String)                               
    status_text = Column('status_text', String)                               
    status_emoji = Column('status_emoji', String)                               
    avatar_hash = Column('avatar_hash', String)                               
    first_name = Column('first_name', String)                               
    last_name = Column('last_name', String)                               
    image_24 = Column('image_24', String)                               
    image_32 = Column('image_32', String)                               
    image_48 = Column('image_48', String)                               
    image_72 = Column('image_72', String)                               
    image_192 = Column('image_192', String)                               
    image_512 = Column('image_512', String)                               
    team = Column('team', String)        

    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.deleted = data.get('deleted', False)

        self.tz = data.get('tz', '')
        self.tz_label = data.get('tz_label', '')
        self.tz_offset = data.get('tz_offset', 0)
        self.is_admin = data.get('is_admin', False)
        self.is_owner = data.get('is_owner', False)
        self.is_primary_owner = data.get('is_primary_owner', False)
        self.is_restricted = data.get('is_restricted', False)
        self.is_ultra_restricted = data.get('is_ultra_restricted', False)
        self.is_bot = data.get('is_bot', False)
        self.updated = data.get('updated', 0)
        self.is_app_user = data.get('is_app_user', False)

        self.title = data.get('profile', {}).get('title', '')
        self.phone = data.get('profile', {}).get('phone', '')
        self.skype = data.get('profile', {}).get('skype', '')
        self.real_name = data.get('profile', {}).get('real_name', '')
        self.real_name_normalized = data.get('profile', {}).get('real_name_normalized', '')
        self.display_name = data.get('profile', {}).get('display_name', '')
        self.display_name_normalized = data.get('profile', {}).get('display_name_normalized', '')
        # self.fields = data.get('fields', '')
        self.status_text = data.get('profile', {}).get('status_text', '')
        self.status_emoji = data.get('profile', {}).get('status_emoji', '')
        self.avatar_hash = data.get('profile', {}).get('avatar_hash', '')
        self.first_name = data.get('profile', {}).get('first_name', '')
        self.last_name = data.get('profile', {}).get('last_name', '')
        self.image_24 = data.get('profile', {}).get('image_24', '')
        self.image_32 = data.get('profile', {}).get('image_32', '')
        self.image_48 = data.get('profile', {}).get('image_48', '')
        self.image_72 = data.get('profile', {}).get('image_72', '')
        self.image_192 = data.get('profile', {}).get('image_192', '')
        self.image_512 = data.get('profile', {}).get('image_512', '')
        self.team = data.get('profile', {}).get('team', '')

    def __repr__(self):
        return "<UserData({0}, {1})>".format(self.id, self.real_name)



def parse_users(session, data_path):
    json_path = data_path + '/users.json'
    data = json.load(open(json_path))
    for user in data:
        session.add(UserData(user))
    session.commit()


def parse_messages_get_fields(data_path):
    json_path = data_path + '/users.json'
    fields_ods = {'skype' : 'Xf0DANL9SL', 'github' : 'Xf3WC3HJMR' } 
    data = json.load(open(json_path))
    with open('fields.csv', 'w') as f:
        for user in data:
            skype = ''
            github = ''
            if user['profile'].get('fields', ''):
                if fields_ods['skype'] in user['profile']['fields']:
                    skype = user['profile']['fields'][fields_ods['skype']]
                    if skype['alt'] != '':
                        skype = skype['alt']
                    else:
                        skype = skype['value']
                if fields_ods['github'] in user['profile']['fields']:
                    github = user['profile']['fields'][fields_ods['github']]
                    if github['alt'] != '':
                        github = github['alt']
                    else:
                        github = github['value']
            f.write('"' + '","'.join([user['id'], user['name'], user['profile']['title'], 
                user['profile'].get('real_name_normalized', ''), 
                user['profile'].get('first_name', ''), user['profile'].get('last_name', ''), 
                skype, github]) + '"\n')
                

if __name__ == '__main__':
    parse_messages_get_fields('../data/users.json')