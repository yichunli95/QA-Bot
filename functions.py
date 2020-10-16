#!/usr/bin/env python3
import io
import nltk
import re


def open_document(file_path):
    with io.open(file_path, 'r', encoding='utf8') as f:
        document = f.read()
    document = re.sub('[\n]+', '. ', document)
    return document


def tokenize_sentence(document):
    return nltk.sent_tokenize(document)


def tokenize_word(sentence):
    return nltk.word_tokenize(sentence)


def pos_tag(token):
    # token: list of words in a sentence
    return nltk.pos_tag(token)


# if __name__ == '__main__':
#     # download tagger information
#     # nltk.download('averaged_perceptron_tagger')
#     document = open_document("../noun_counting_data/a1.txt")
#     sentences = tokenize_sentence(document)
#     tokens = [tokenize_word(sentence) for sentence in sentences]
#     pos_tags = [pos_tag(token) for token in tokens]

