#!/usr/bin/env python3
import io
import nltk
import re
import spacy


def open_document(file_path):
    with io.open(file_path, 'r', encoding='utf8') as f:
        document = f.read()
    document = re.sub('[\n]+', ' . ', document)
    return document


def tokenize_sentence(document):
    return nltk.sent_tokenize(document)


def tokenize_word(nlp, sent):
    sentence = nlp(sent)
    return [token for token in sentence]


def pos_tag(nlp, sent):
    sentence = nlp(sent)
    return [token.pos_ for token in sentence]


# if __name__ == '__main__':
#     nlp = spacy.load('en_core_web_sm')
#     document = open_document("../noun_counting_data/a1.txt")
#     sentences = tokenize_sentence(document)
#     for sent in sentences:
#         print(tokenize_word(nlp, sent))
#         print(pos_tag(nlp, sent))
#         sentence = nlp(sent)
#         # noun chunks
#         print([nc for nc in sentence.noun_chunks])
#
#         # NER
#         print([(ent.text, ent.label_) for ent in sentence.ents])
