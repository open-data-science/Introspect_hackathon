# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import codecs
from collections import defaultdict

import pymorphy2
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
import stop_words

from tokenizer import tokenize, preprocessing
from slack_data_loader import SlackLoader


morph = pymorphy2.MorphAnalyzer()

QUESTION_WORD_LEMMAS = ("как", "как-то", "какой", "какой-то", "зачем", "почему", "когда", "кто", "где",
                        "когда", "куда", "куда-то", "чот")
QUESTION_WORDS = ("подскажите", "посоветуйте", "дайте", "киньте", "кинте")
STOP_WORDS = stop_words.get_stop_words("russian")
PUNCTUATION = ['.', ',', ';', ':', '!', '?', '-', '<', '>', '(', ')', '<-', '`', '::', '//', '/', '>:',
               '{', '}', '--', '(<', '\\', '}]', ']', '[', '))', '>>', '..', '...', '==', '```', '#',
               '~', '"', '%)', ';<', '|', '!!', 'slightly_smiling_face', 'simple_smile', 'http',
               'https', ':/', 'smile', 'www.', 'com', 'ru', 'org', 'ru.', "'"]


def is_question(tokens):
    is_q = False
    for i, t in enumerate(tokens):
        if t in QUESTION_WORDS:
            is_q = True
        t = morph.parse(t)[0].normal_form
        tokens[i] = t
        if t in QUESTION_WORD_LEMMAS:
            is_q = True
    return is_q


def prepare_data():
    print('Loading data...')
    loader = SlackLoader('opendatascience Slack export May 20 2017', is_sorted=False,
                         only_channels=['nlp', 'deep_learning', 'datasets', 'sequences_series', 'bayesian', '_meetings',
                                        'edu_academy', 'edu_books', 'visualization',
                                        'hardware', 'reinforcement_learnin', 'theory_and_practice'])

    print('Converting data...')
    channel_messages = []
    previous_channel = ''
    label_id = 0
    with codecs.open('vw_data_train.vw', 'w', encoding='utf8') as vw_train:
        with codecs.open('vw_data_test.vw', 'w', encoding='utf8') as vw_test:
            for m in loader.messages:
                tokens = [t for t in tokenize(preprocessing(m['text']))
                          if t not in PUNCTUATION and not t.startswith('@')]
                # take only questions
                if is_question(tokens):
                    if previous_channel != m['channel']:
                        previous_channel = m['channel']
                        if channel_messages:
                            label_id += 1
                            train, test = train_test_split(channel_messages, test_size=0.15)
                            for t in train:
                                text = t[1].replace(':', ';').replace('|', '/')
                                vw_train.write('%s | %s\n' % (label_id, text))
                            for t in test:
                                text = t[1].replace(':', ';').replace('|', '/')
                                vw_test.write('%s | %s\n' % (label_id, text))
                            channel_messages = []
                    tokens = [t for t in tokens if t not in STOP_WORDS]
                    if len(tokens) > 3:
                        channel_messages.append((m['channel'], ' '.join(tokens)))

            # a last channel data
            label_id += 1
            train, test = train_test_split(channel_messages, test_size=0.15)
            for t in train:
                text = t[1].replace(':', ';').replace('|', '/')
                vw_train.write('%s | %s\n' % (label_id, text))
            for t in test:
                text = t[1].replace(':', ';').replace('|', '/')
                vw_test.write('%s | %s\n' % (label_id, text))


'''def convert_to_vw_format():
    file_name = 'fasttext_data.txt'
    file_name_vw = file_name.split('.')[0] + '.vw'
    previous_label = ''
    label_id = 0
    with codecs.open(file_name, 'r', encoding='utf-8') as f:
        with codecs.open(file_name_vw, 'w', encoding='utf-8') as f_out:
            for sentence in f:
                try:
                    label, text = sentence.strip().split(' ', 1)
                    if previous_label != label:
                        label_id += 1
                        previous_label = label
                    text = text.replace(':', ';').replace('|', '/')
                    f_out.write('%s | %s\n' % (label_id, text))
                except Exception as e:
                    print(e)'''


def analyze():
    total = 0
    correct = 0
    labels_total = defaultdict(int)
    labels_correct = defaultdict(int)
    y_true = []
    y_pred = []
    with codecs.open('vw_data_test.vw', encoding='utf-8') as f:
        with codecs.open('vw_data_test.vw.pred', encoding='utf-8') as f_pred:
            for l in f:
                try:
                    label_pred = f_pred.readline().strip()
                    label, text = l.split(' | ')
                    y_pred.append(int(label_pred))
                    y_true.append(int(label))
                    if (int(label) in [2, 8] and int(label_pred) in [2, 8]) and label != label_pred:
                        if len(text.strip().split(' ')) <= 3:
                            print('%s - %s' % (label, text.strip()))
                    if label == label_pred:
                        correct += 1
                        labels_correct[label] += 1
                    total += 1
                    labels_total[label] += 1
                except:
                    pass

    print('Accuracy total %s' % (correct / float(total)))
    for l, v in labels_correct.iteritems():
        print('Accuracy for label %s: %s' % (l, v / float(labels_total[l])))

    print(confusion_matrix(y_true, y_pred))

if __name__ == '__main__':
    # prepare_data()

    # here we train a model and predict on test data: bash vw.sh
    from subprocess import call
    call(["bash", "vw.sh", "vw_data_train.vw", "vw_data_test.vw", "0.05", "2"])

    analyze()
