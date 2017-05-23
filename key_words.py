import json
import glob
import os
import datetime
import re
import pymorphy2
import pandas as pd
from nltk import word_tokenize

morph = pymorphy2.MorphAnalyzer()


#from slack_export import SlackExport, normalize_links
from Introspect_hackathon.slack_data_loader import SlackLoader


def start():
	# data_folder = ‘/Users/alex/Documents/ODS/oct_4_2016_dump’
	data_folder = "ODS_dump_Mar_10_2017"
	
	#ods = SlackExport(data_folder)
	ods = SlackLoader(data_folder, exclude_channels=["_random_flood", "career"])

	df_msg = pd.DataFrame.from_records(ods.messages)
	
	return df_msg


def cleanUsernames(str):
	re.sub(r"<@", "")


def lemm(st):
	if st == '':
		return ''
	else:
		return morph.parse(st)[0].normal_form



from stop_words import get_stop_words
from string import punctuation

punct = set(punctuation)
punct.add(' > ')
punct.add(' < ')

stop_words = set(get_stop_words('ru'))

print(':' in punct)

def pars(text):
	target = []
	print(len(text))
	count = 0
	for supidx, txt in enumerate(text):
		if supidx == 100:
			break
		# print(txt)
		count += 1
		for line in txt.split('\n'):
			# if len(grade.findall(line)) != len([l for l in line]):
			snt = re.split("\.+ |, | ! | \? |  \( |\) | - ", line)
			bigram = []
			words = []
			trigram = []
			for s in snt:
				spl = s.split(' ')
				if len(s) > 1:
					for i in range(0, (len(spl) - 1)):
						if ((spl[i] not in stop_words) and (spl[i + 1] not in stop_words)
							and spl[i].isdigit() == False and spl[i + 1].isdigit() == False
							and (spl[i + 1] not in punct) and (spl[i] not in punct)):
							bigram.append(str(lemm(spl[i])) + ' ' + str(lemm(spl[i+1])))

					for i in range(0, (len(spl) - 2)):
						if ((spl[i] not in stop_words) and (spl[i + 1] not in stop_words)
							and (spl[i + 2] not in stop_words)
							and spl[i].isdigit() == False and spl[i + 1].isdigit() == False
							and spl[i + 2].isdigit() == False
							and (spl[i + 1] not in punct) and (spl[i] not in punct)
							and (spl[i + 2] not in punct)):
							trigram.append(str(lemm(spl[i])) + ' ' + str(lemm(spl[i + 1])) + ' '+str(lemm(spl[i+2])))

					for i in range(0, (len(spl))):
						if (spl[i] not in stop_words) and spl[i].isdigit() == False:
							words.append(str(lemm(spl[i])))
				trg = bigram + words + trigram
				target.append(trg)
				#print(count, trg)
	return target

def clean(matrix):
	return pars(matrix['text'])


def loadCommonLang(datapath="corpus_freq_dict.csv"):
	fCorpus = open(datapath, encoding="UTF-8")
	lines = fCorpus.readlines()
	
	vocabulary = {}
	for i, line in enumerate(lines):
		if line != "\n":
			sample = re.sub("\n", "", line)
			sample = sample.split(",")
			vocabulary[sample[0]] = int(sample[1])
	
	return vocabulary


def countAllWordsVocab(vocabulary):
	cnt = 0
	for word in vocabulary:
		cnt += vocabulary[word]
	
	return cnt


def strange(m, m1):  # для 2 массивов слов
	f = len(m)
	f1 = countAllWordsVocab(m1)

	mass = []
	for word in set(m):
		if word in m1:
			res = round((m.count(word) / f) / (m1[word] / f1), 4)
			mass.append((word, res))
		else:
			mass.append((word, 75.))
	return mass


def oneList(text):
	res = []
	for i, sentence in enumerate(text):
		res += sentence
	
	return res


import pymysql.cursors, re


def getMySQLData(limit=1000000, sql="SELECT ttext FROM %s LIMIT %s"):
	connection = pymysql.connect(host='localhost', user='root', password='root', db='sys', charset='utf8mb4',
								 cursorclass=pymysql.cursors.DictCursor)
	
	try:
		with connection.cursor() as cursor:
			#sql = "SELECT ttext FROM %s LIMIT %s"
			cursor.execute(sql, limit)
			
			result = cursor.fetchall()
			data = []
			for i, item in enumerate(result):
				try:
					if item['ttext'] != None:
						data.append(re.sub("\n", " ", item['ttext']))
				except Exception:
					print("%d %s" % (i, item))
			
			return data
	finally:
		connection.close()


def loadTwitterDict():
	from collections import Counter
	# limit = 1000000
	limit = 111000
	negdata = getMySQLData(limit, "SELECT ttext FROM `sortneg` LIMIT %s")
	posdata = getMySQLData(limit, "SELECT ttext FROM `sortpos` LIMIT %s")
	limit = 1000000
	neutraldata = getMySQLData(limit, "SELECT ttext FROM `sentiment` LIMIT %s")
	
	data = negdata + posdata + neutraldata
	

	#sentences = pars(data)
	sentences = []
	for i, text in enumerate(data):
		sentences += re.split("\.+ |, | ! | \? |  \( |\) | - ", text)

	words = []
	for i, sentence in enumerate(sentences):
		words += word_tokenize(sentence)
	
	#words = []
	#for i, sentence in enumerate(sentences):
	#	words += sentence

	from nltk import collections
	counts = dict(Counter(words))
	return counts


def wordsChoose(dic, barrier=5.):
	res = []
	for i, word in enumerate(dic):
		if word[1] > barrier:
			res.append(word)
	return res


def writeData(data, datapath='strange.csv'):
	import csv
	with open(datapath, "w+", encoding="UTF-8") as f:
		a = csv.writer(f)
		for i, word in enumerate(data):
			a.writerow(word)


if __name__ == "__main__":
	counts = loadTwitterDict()
	#vocab = loadCommonLang()
	df_msg = start()
	lemmatized = clean(df_msg)
	onelst = oneList(lemmatized)
	strangeness = strange(onelst, counts)
	ranged_strange_words = wordsChoose(strangeness)
	writeData(ranged_strange_words, datapath='strange.csv')
