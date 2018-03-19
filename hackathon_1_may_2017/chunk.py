import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import os
import datetime
import time

import itertools

from slack_data_loader import SlackLoader

SECS_IN_DAY = 60 * 60 * 24

# this class wrap time by daily activity distribution 
class TimeDistance:
    
    def calc_dist(self, times):
        day_times = times % SECS_IN_DAY
        hist, ranges = np.histogram(day_times, range=(0, SECS_IN_DAY), bins=self.bins)
        total_count = hist.sum()
        normalized_hist = hist / self.total_count
        ranges = ranges.astype(int)[:-1]
        dist = dict(zip(ranges, normalized_hist))
        mean = normalized_hist.mean()
        return (mean, dist)
    
    
    def get_time_range(self, ts):
        dt = datetime.datetime.fromtimestamp(ts)
        return str(dt.year) + str(int(dt.month / 6))
    
    def init_distribution(self, times):
        # split by years somehow
        self.bins = 100
        self.time_step = int(SECS_IN_DAY / self.bins)
        self.total_count = times.size
        
        datetimes = map(self.get_time_range, times)
        zp = zip(datetimes, times)
        grps = itertools.groupby(zp, key=lambda x: x[0])

        time_groups = list([ (k, np.array([y for x,y in g]) ) for k,g in grps])
        
        meanes = []
        dists = []
        for key, group_times in time_groups:
            mean, dist = self.calc_dist(group_times)
            meanes.append( (key, mean) )
            dists.append( (key, dist) )
        
        self.dist = dict(dists)
        self.mean = dict(meanes)
        
        return self
    
    def get_range_start(self, ts):
        return int(ts % SECS_IN_DAY / self.time_step) * self.time_step
    
    def get_dist(self, ts):
        curr_range = self.get_range_start(ts)
        return self.dist[self.get_time_range(ts)][curr_range]
    
    def get_mean(self, ts):
        return self.mean[self.get_time_range(ts)]
        
    def distance(self, ts1, ts2):
        max_ts = max(ts1, ts2)
        min_ts = min(ts1, ts2)
        curr = min_ts
        dist = 0.0
        diff = max_ts - min_ts
        if diff > SECS_IN_DAY:
            secs = int(diff / SECS_IN_DAY) * SECS_IN_DAY
            dist += secs * self.get_mean(curr)
            curr += secs
        while curr < max_ts:
            time_to_next_range = self.time_step - curr % self.time_step
            time_to_end = max_ts - curr
            min_time = min(time_to_end, time_to_next_range)
            curr += min_time
            dist += self.get_dist(curr) * min_time
        return dist

class Chunker:
    def split_by_threshold(self, difs, threshold):
        res = []
        start = 0
        curr = difs
        while len(curr) > 0:
            group_len = len(list(itertools.takewhile(lambda x: x < threshold, curr)))
            res.append(range(start, start + group_len + 1))
            curr = curr[group_len + 1:]
            start = start + group_len + 1
        return res

    def cluster_time_series(self, timeObj, times, threshold = 100.0):
        time_difs = np.zeros(times.size - 1)
        for i in range(0, times.size - 2):
            time_difs[i] = timeObj.distance(times[i], times[i + 1])
        chunks = self.split_by_threshold(time_difs, threshold)
        return chunks
    
    def merge_with_threads(self, chunks, threads):
        for thread in threads:
            chunks = list(filter(lambda x: not (x[0] <= thread[0] <= x[-1] or x[0] <= thread[-1] <= x[-1]), chunks))
        chunks += threads
        return sorted(chunks, key=lambda x: x[0])

    def get_groups(self, data, threshold = 30):
        times = np.array(list(map(lambda x: x['ts'], data.messages)))
        timeObj = TimeDistance().init_distribution(times)
        chunks = self.cluster_time_series(timeObj, times, threshold=threshold)
        chunk_lengthes = np.array(list(map(len, chunks)))
        threads = data.find_threads()
        chunks = self.merge_with_threads(chunks, threads)
        for chunk in chunks:
            yield [ data.messages[i] for i in chunk ]

