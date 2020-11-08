#!/usr/bin/env python3
import io
import nltk
import re
import spacy
from svo import nlp, findSVOs


def open_document(file_path):
    with io.open(file_path, 'r', encoding='utf8') as f:
        document = f.read()
    document = re.sub('[\n]+', ' . ', document)
    return document


def tokenize_sentence(document):
    return nltk.sent_tokenize(document)


def find_verb(tok):
    head = tok.head
    while head.pos_ != "VERB" and head.head != head:
        head = head.head
    return head


def generate_why_dict(token, word_token):
    why_key_word = ['because', 'as a result']
    why_dict = {}
    for key in why_key_word:
        if key in word_token:
            index = word_token.index(key)
            tok = token[index]
            v = find_verb(tok).text
            if v not in why_dict:
                why_dict[v] = []
            why_dict[v].append(key)
    return why_dict


def generate_when_and_where_dict(token, word_token):
    when_key_word = ['TIME', 'DATE']
    where_key_word = ['FAC', 'GPE', 'LOC']
    when_dict = {}
    where_dict = {}
    ner = [(tok.text, tok.label_) for tok in token.ents]
    ner_dict = {}
    for entity in ner:
        ner_dict[entity[0].lower()] = entity[1]

        if entity[1] in when_key_word:
            key = entity[0].lower()
            if ' ' in key:
                key = key.split(' ')[0]
            if '-' in key:
                key = key.split('-')[0]
            index = word_token.index(key)
            tok = token[index]
            v = find_verb(tok).text
            if v not in when_dict:
                when_dict[v] = []
            when_dict[v].append(entity[0])

        if entity[1] in where_key_word:
            key = entity[0].lower()
            if ' ' in key:
                key = key.split(' ')[0]
            if '-' in key:
                key = key.split('-')[0]
            index = word_token.index(key)
            tok = token[index]
            v = find_verb(tok).text
            if v not in where_dict:
                where_dict[v] = []
            where_dict[v].append(entity[0])
    return ner_dict, when_dict, where_dict


if __name__ == '__main__':
    document = open_document("../data/set1/a1.txt")
    sentences = tokenize_sentence(document)
    sentences = sentences[0:1]
    who_key_word = ['he', 'she', 'they', 'him', 'her', 'them']

    for sent in sentences:
        sent = "In 2006, Viz released ten DVDs based around individual Pokémon in celebration of Pokémon's 10th anniversary in the United States. "
        token = nlp(sent)
        print("Sentence: ", token)
        word_token = [tok.lower_ for tok in token]

        why_dict = generate_why_dict(token, word_token)
        ner_dict, when_dict, where_dict = generate_when_and_where_dict(token, word_token)

        result = findSVOs(token)
        # print("why: ", why_dict)
        # print("when: ", when_dict)
        # print("where: ", where_dict)
        # print("svo:", result)
        print("Questions:")
        for entity in result:
            subject, verb, object = entity
            # generate question about verb
            if verb in why_dict:
                print("Why did " + subject + " " + verb + " " + object + "?")
            if verb in when_dict:
                print("When did " + subject + " " + verb + " " + object + "?")
            if verb in where_dict:
                print("Where did " + subject + " " + verb + " " + object + "?")

            # generate question about subject
            question_type = "What"
            for k, v in ner_dict.items():
                if k in subject.lower() and v == 'PERSON':
                    question_type = "Who"
                    break

            for key in who_key_word:
                if subject.lower() == key:
                    question_type = "Who"
                    break
            print(question_type + " " + verb + " " + object + "?")


