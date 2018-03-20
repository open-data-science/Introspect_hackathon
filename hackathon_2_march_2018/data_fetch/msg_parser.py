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

class Channel(Base):
    __tablename__ = 'imported_channel'

    name = Column('name', String, primary_key=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Channel({0})>".format(self.name)


class Message(Base):
    __tablename__ = 'imported_messages'

    channel = Column('channel', String, primary_key=True)
    ts = Column('ts', String, primary_key=True)

    type = Column('type', String)
    text = Column('text', String)
    user = Column('user', String)
    thread_ts = Column('thread_ts', String)
    parent_user_id = Column('parent_user_id', String)
    subtype = Column('subtype', String)
    # reactions = Column('reactions', String) table
    # edited = Column('edited', String) later
    # attachments = Column('attachments', String) table
    reply_count = Column('reply_count', Integer)
    # replies = Column('replies', String) table
    unread_count = Column('unread_count', Integer)
    bot_id = Column('bot_id', String)
    username = Column('username', String)
    # file = Column('file', String)

    def __init__(self, channel, data):
        self.channel = channel
        self.ts = data.get('ts', '')

        self.type = data.get('type', '')
        self.text = str(data.get('text', ''))
        self.user = data.get('user', '')
        self.thread_ts = data.get('thread_ts', '')
        self.parent_user_id = data.get('parent_user_id', '')
        self.subtype = data.get('subtype', '')
        # self.reactions = data.get('reactions', '')
        # self.edited = data.get('edited', '')
        # self.attachments = data.get('attachments', '')
        self.reply_count = data.get('reply_count', '')
        self.replies = data.get('replies', '') 
        self.unread_count = data.get('unread_count', '')
        self.bot_id = data.get('bot_id', '')
        self.username = data.get('username', '')

    def __repr__(self):
        return "<Message({0}, {1}, {2})>".format(self.channel, self.date, self.index)


def parse_messages(session, data_path):
    # c = Counter()  
    dirs = [e.name for e in os.scandir(data_path) if e.is_dir()]
    # msg_keys = set()
    for dir in dirs:
        pprint(data_path + os.sep + dir)
        # if dir != 'welcome':
        #     continue
        for d, dirs, files in os.walk(data_path + os.sep + dir):
            channel = d.split('/')[-1]
            session.add(Channel(channel))
            for f in files:
                path = os.path.join(d, f)
                # print(path)
                data = json.load(open(path))
                for msg in data:
                    session.add(Message(channel, msg))
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
#     parse_messages('../data')
#     # print(c.most_common(100))
