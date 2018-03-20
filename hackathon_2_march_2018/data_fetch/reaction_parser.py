# -*- coding: utf-8 -*-

import os, logging
import json
from pprint import pprint
from collections import Counter
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Table, Column, Integer, String, Boolean, DateTime, Date, MetaData, ForeignKey
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

Base = declarative_base()

class Reaction(Base):
    __tablename__ = 'imported_reactions'

    channel = Column('channel', String, primary_key=True)
    message_ts = Column('message_ts', String, primary_key=True)
    user_id = Column('user_id', String, primary_key=True)
    name = Column('name', String, primary_key=True)

    def __init__(self, channel, message_ts, user_id, name):
        self.channel = channel
        self.message_ts = message_ts
        self.user_id = user_id
        self.name = name

    def __repr__(self):
        return "<Reaction({0}, {1}, {2})>".format(self.name, self.message_ts, self.user_id)


class ReactionCount(Base):
    __tablename__ = 'imported_reactions_count'

    channel = Column('channel', String, primary_key=True)
    message_ts = Column('message_ts', String, primary_key=True)
    name = Column('name', String, primary_key=True)
    count = Column('count', Integer)

    def __init__(self, channel, message_ts, name, count):
        self.channel = channel
        self.message_ts = message_ts
        self.name = name
        self.count = count

    def __repr__(self):
        return "<Reaction({0}, {1}, {2})>".format(self.name, self.message_ts, self.count)


def parse_reactions(session, data_path):
    # c = Counter()  
    dirs = [e.name for e in os.scandir(data_path) if e.is_dir()]
    # msg_keys = set()
    for dir in dirs:
        pprint(data_path + os.sep + dir)
        # if dir != 'welcome':
        #     continue
        for d, dirs, files in os.walk(data_path + os.sep + dir):
            channel = d.split('/')[-1]
            # session.add(Channel(channel))
            for f in files:
                path = os.path.join(d, f)
                # print(path)
                data = json.load(open(path))
                for msg in data:
                    if 'reactions' in msg.keys():
                        for reaction in msg['reactions']:
                            for user in reaction['users']:
                                session.add(Reaction(channel, msg['ts'], user, reaction['name']))
                    # c.update(msg.keys())
                    # for key in msg.keys():
                    #     msg_keys.add(key)
                    # session.add()
        session.commit()
    # pprint(msg_keys)
    # pprint(c.most_common(60))
    # print(len(msg_keys), '\n')


def parse_reactions_count(session, data_path):
    # c = Counter()  
    dirs = [e.name for e in os.scandir(data_path) if e.is_dir()]
    # msg_keys = set()
    for dir in dirs:
        pprint(data_path + os.sep + dir)
        # if dir != 'welcome':
        #     continue
        for d, dirs, files in os.walk(data_path + os.sep + dir):
            channel = d.split('/')[-1]
            # session.add(Channel(channel))
            for f in files:
                path = os.path.join(d, f)
                # print(path)
                data = json.load(open(path))
                for msg in data:
                    if 'reactions' in msg.keys():
                        for reaction in msg['reactions']:
                            session.add(ReactionCount(channel, msg['ts'], reaction['name'], reaction['count']))
                    # c.update(msg.keys())
                    # for key in msg.keys():
                    #     msg_keys.add(key)
                    # session.add()
        session.commit()
    # pprint(msg_keys)
    # pprint(c.most_common(60))
    # print(len(msg_keys), '\n')

# if __name__ == '__main__':
#     Base.metadata.create_all(engine)
#     parse_reactions_count('../data')
