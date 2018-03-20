# -*- coding: utf-8 -*-

import os, logging
import json
from pprint import pprint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Table, Column, Integer, String, Boolean, DateTime, MetaData, ForeignKey
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)
local_name = 'sqlite:///../ods-slack.db'
remote_name = 'postgres://usgbqmayetwlrv:a8b6a60b922bd6d08c3e94fa41eac937f71ed3bc4afade4995a3bdf5d54e36ca@ec2-54-247-81-88.eu-west-1.compute.amazonaws.com:5432/d7942vtj104cpv'
engine = create_engine(local_name, echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
dump_ODS_path = '../data'

import users_parser
import msg_parser
import reaction_parser

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    users_parser.Base.metadata.create_all(engine)
    msg_parser.Base.metadata.create_all(engine)
    reaction_parser.Base.metadata.create_all(engine)
    Base.metadata.create_all(engine)

    session = Session()

    # users_parser.UserData.__table__.drop(engine)
    # msg_parser.Channel.__table__.drop(engine)
    # msg_parser.Message.__table__.drop(engine)
    # reaction_parser.Reaction.__table__.drop(engine)
    # reaction_parser.ReactionCount.__table__.drop(engine)

    users_parser.parse_users(session, dump_ODS_path)
    msg_parser.parse_messages(session, dump_ODS_path)
    reaction_parser.parse_reactions(session, dump_ODS_path)
    reaction_parser.parse_reactions_count(session, dump_ODS_path)

