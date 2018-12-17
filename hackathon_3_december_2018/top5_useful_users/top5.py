#Script that returns a pickle file "top5.pkl" with a dictionary of top5 most useful posters in channels mentioned in "selected_channels" list. Path to message dump is defined by
#dumppath variable. For easier additional prototyping "tetelias_hackathon3.ipynb" is provided
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

from collections import defaultdict
from utils import *

import datetime
import glob
import json
import numpy as np
import os
import pandas as pd
import pickle
import re

#function, that returns list of reactions from an element of "reactions" Series
def reactions_list(dictlist):
    reslist = []
    if dictlist == '':
        res = ''
    else:
        for d in dictlist:
            reslist.append(d['name'])
        res = ' '.join(reslist)
    return res

#List of channels to get top5 useful posters for
selected_channels = ['bayesian', 'deep_learning', 'lang_cpp', 'lang_python', 'mltrainings_beginners', 'nlp', 'recommender_systems', 'reinforcement_learnin', 'theory_and_practice']
#Path to the ODS message dump
dumppath = 'shared/latest_dump'
#good_reactions = ['+1', '+1::skin-tone-2', '+1::skin-tone-3', '+1::skin-tone-4', '+1::skin-tone-6', '100','heavy_plus_sign', 'omgtnx','tnx']
good_reactions = ['100', 'heavy_plus_sign', 'omgtnx','tnx']
kek_reactions = ['kekeke','trollface']

patternAdv = '|'.join(ADVICE_WORDS)
patternGR = '|'.join(good_reactions)
patternKR = '|'.join(kek_reactions)
patternQue = '|'.join(QUESTION_WORD_LEMMAS+QUESTION_WORDS)

if __name__ == '__main__':
    
    top5_dict = {}
    
    for channel in selected_channels:
        loader = SlackLoader(dumppath,only_channels=channel)

        #Creating Pandas DF, then cutting off posts from 2016 and earlier
        df_msg = pd.DataFrame.from_records(loader.messages)
        df_msg = df_msg[df_msg.dt > datetime.datetime(2017, 1, 1)]

        df_msg.text = df_msg.text.str.lower()

        #Creating temp DF with posts outside of threads, finding texts of previous and next posts and question posts among those that don't have their own threads
        #then merging with original DF
        df_msg2 = df_msg[df_msg.thread_ts.isnull()|(df_msg.thread_ts == df_msg.ts)].copy()
        df_msg2['text_prev'] = df_msg2.text.shift()
        df_msg2['text_next'] = df_msg2.text.shift(-1)
        df_msg2['open_question'] = np.where(df_msg2['text'].str.contains(patternQue, case=False)&(df_msg2['thread_ts'].isnull()),
                                            1,
                                            0)
        df_msg2['after_open_question'] = df_msg2['open_question'].shift(1).fillna(0)
        df_msg = df_msg.merge(df_msg2[['dt','text_prev','text_next','open_question','after_open_question']],how='left',on='dt')

        #Creating a flag for posts with threads
        df_msg['thread_question'] = np.where(df_msg['text'].str.contains(patternQue, case=False)&(df_msg['ts']==df_msg['thread_ts']),
                                         1,
                                         0)

        #Creating measure of good posts, first for those that have 'спасибо' in the next one, indicating this one was a helpful answer
        df_msg['useful'] = np.where(df_msg.thread_ts.isnull() & df_msg.text_next.str.contains('спасибо') & ~df_msg.text_next.str.contains('заранее'),
                                    1,
                                    0)
        #Post after the question that is not a question itself is considered an answer
        df_msg['useful'] = df_msg['useful'] + df_msg['after_open_question']*(~df_msg['thread_question'])*(~df_msg['open_question'])
        
        #Columns with all reactions in a single string for each post is created
        df_msg['reactions'] = np.where(df_msg['reactions'].isnull(),
                                       '',
                                       df_msg['reactions'])   
        df_msg['reactionslist'] = df_msg['reactions'].apply(reactions_list)
        
        #All posts inside threads are counted as answers, except those with "kek" tonality are discarded and those marked with good reactions are extra rewarded
        question_threads = set(df_msg[df_msg['thread_question']==1].thread_ts.unique().tolist())
        df_msg['useful'] = df_msg['useful'] + (df_msg['thread_ts'].isin(question_threads)&(df_msg['thread_ts']!=df_msg['ts'])&(df_msg[df_msg.parent_user_id != df_msg.user]))
        
        df_msg['useful'] = df_msg['useful'] - 1000*(df_msg['thread_ts'].isin(question_threads)&
                                                    (df_msg['thread_ts']!=df_msg['ts'])&
                                                    df_msg['reactionslist'].str.contains(patternKR, case=False))
        
        df_msg['useful'] = df_msg['useful'] + (df_msg['thread_ts'].isin(question_threads)&
                                               (df_msg['thread_ts']!=df_msg['ts'])&
                                               df_msg['reactionslist'].str.contains(patternGR, case=False))
        
        #All non-relevant posts get 'useful' attribute set to 0
        df_msg['useful'] = (df_msg['useful']>0)*df_msg['useful']
        
        #Returning top5 users with best sum of 'useful' column
        top5 = df_msg[['user', 'useful']].groupby('user').agg('sum').reset_index().sort_values('useful',ascending=False).iloc[:5]['user'].tolist()
        
        top5_dict[channel] = [loader.users[name]['profile']['display_name_normalized'] 
                              if loader.users[name]['profile']['display_name_normalized'] != '' 
                              else loader.users[name]['profile']['display_name'] 
                              for name in top5]
        
    with open('top5.pkl', 'wb') as f_top5:
        pickle.dump(top5_dict, f_top5)
