# -*- coding: utf-8 -*-
import re

GROUPING_SPACE_REGEX = re.compile(r'([^@\w_\-])', re.UNICODE | re.MULTILINE)

ALPHABET = re.compile(u'[A-Za-zА-ЯЁа-яё]')

# special tokens to be found before system processing
web_address_re = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
email_re = re.compile(u'[а-яёА-ЯЁA-Za-z0-9.+_-]+@[^@]+\.[a-zA-Zа-яёА-ЯЁ]+')
number_re = re.compile(u'(^|[^\w\-])[+\-]*[0-9]+[0-9 =―—–_:.,/x×\-*]*[\-ыхейюомуя]*([^\w\-]|$)', re.UNICODE)


def simple_word_tokenize(text, _split=GROUPING_SPACE_REGEX.split):
    """
    Split text into tokens. Don't split by a hyphen and an underscore.
    Preserve punctuation, but not whitespaces.
    """
    return [t for t in _split(text) if t]


def replace_number(match_obj):
    return u'%sNUM%s' % (match_obj.group(1), match_obj.group(2))


def tokenize(text):
    inp_tokens = simple_word_tokenize(text)
    tokens_len = len(inp_tokens)
    output_tokens = []
    # combine some tokens together: contractions, smileys, emoticons, etc.
    for index, token in enumerate(inp_tokens):
        # contractions with length < 5
        if token in u'.' and 0 < index < tokens_len - 1 and inp_tokens[index + 1] not in u'.?-–—)\'"”»' and \
           output_tokens and len(output_tokens[-1]) < 5:
            output_tokens[-1] += token
        # english contractions
        elif token in [u's', u've', u'm', u'll', u're', u'd', u't'] and index > 0 and inp_tokens[index - 1] in u'\'`':
            output_tokens[-1] += token
        # cut a hyphen off from the beginning of a word
        elif token[0] == u'-' and len(token) > 1 and ALPHABET.match(token[1]):
            output_tokens.append(u'-')
            output_tokens.append(token[1:])
        # !? or ?!
        elif token in u'?!' and index > 0 and inp_tokens[index - 1] in u'?!':
            if len(output_tokens[-1]) < 2:
                output_tokens[-1] += token
        # repetition of dots, question marks, slashes, etc
        elif token in u'.,?!^*/=:;«»"“”-–—@+()_❤☀' and index > 0 and inp_tokens[index - 1] == token:
            if len(output_tokens[-1]) < 2:
                output_tokens[-1] += token
        # smileys, emoticons
        elif token in u'-–—/_{}()[]<>`*:^=DP' and index > 0 and inp_tokens[index - 1] and \
                inp_tokens[index - 1] in u'/`^:{}()[]<>*%=;-–—_':
            output_tokens[-1] += token
        else:
            if not token.isspace():
                output_tokens.append(token)
    return output_tokens


def preprocessing(sent):
    # replace URL address on URL token, e-mail on EMAIL and numbers on NUM before tokenizing
    # sent = web_address_re.sub('URL', )  # number_re.sub(replace_number, sent)
    sent = email_re.sub('EMAIL', sent).replace('\n', '').strip().lower()
    sent = sent.replace(u'ё', u'е').replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>'). \
        replace('&amp;', '&').replace('&apos;', '`').replace('', '').replace('<br>', '')
    return sent

if __name__ == '__main__':
    # test
    import codecs
    from time import time

    total = 0
    error = 0
    with codecs.open('tokens.txt', 'w', encoding='utf-8') as f_out:
        with codecs.open('sentences.txt', 'r', encoding='utf-8') as f:
            start_time = time()
            for sentence in f:
                sentence = sentence.strip()
                if sentence:
                    sentence = preprocessing(sentence)
                    tokens = tokenize(sentence)
                    f_out.write(u' '.join(tokens)+'\n')
            print 'Execution time: %s' % (time() - start_time)
