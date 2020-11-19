#!/usr/bin/python3 -W ignore::DeprecationWarning
# -*- coding:utf8 -*-
#/usr/bin/env python3

#!/usr/bin/env python3

import io
import nltk
import re
import spacy
import random

from . import svo
#from svo import nlp, findSVOs


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
    why_key_word = ['because']
    why_dict = {}
    for key in why_key_word:
        if key in word_token:
            try:
                index = word_token.index(key)
                tok = token[index]
                v = find_verb(tok).text
                if v not in why_dict:
                    why_dict[v] = []
                why_dict[v].append(key)
            except:
                continue
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
            try:
                key = entity[0].lower()
                if ',' in key:
                    key = key.split(',')[0]
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
            except:
                continue

        if entity[1] in where_key_word:
            try:
                key = entity[0].lower()
                if ',' in key:
                    key = key.split(',')[0]
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
            except:
                continue
    return ner_dict, when_dict, where_dict


def generate_questions(document_path):
    document = open_document(document_path)
    sentences = tokenize_sentence(document)
    # sentences = sentences[0:10]
    who_key_word = ['he', 'she', 'they', 'him', 'her', 'them', 'who']
    question_set = set()

    for sent in sentences:
        # sent = "A study showed that of the 58 people who were present when the tomb and sarcophagus were opened, only eight died within a dozen years."
        token = svo.nlp(sent)
        print("Sentence: ", token)
        word_token = [tok.lower_ for tok in token]
        # index = word_token.index("with")
        # print(token[index].pos_, token[index].dep_)
        # print(token[index].head)
        # for e in token[index].lefts:
        #     print(e, e.pos_, e.dep_)
        # for e in token[index].rights:
        #     print(e, e.pos_, e.dep_)
        why_dict = generate_why_dict(token, word_token)
        ner_dict, when_dict, where_dict = generate_when_and_where_dict(token, word_token)

        result = svo.findSVOs(token)
        # print("svo:", result)
        print("Questions:")
        for entity in result:
            subject, subject_tag, negation, verb, object, verb_modifier = entity
            if subject == ' ':
                continue
            print(entity)
            # generate question about verb
            question_tense1 = ''
            what_tense = ''
            tense = verb.tag_
            plural = subject_tag == 'NNS' or subject_tag == 'NNPS'

            verb_str = verb.text
            what_verb = verb.text
            if tense == 'VBD':
                question_tense1 = 'did'
                verb_str = verb.lemma_
            elif tense == 'VBG':
                if plural:
                    question_tense1 = 'are'
                    what_tense = 'are'
                else:
                    question_tense1 = 'is'
                    what_tense = 'is'
            elif tense == 'VBN':
                if plural:
                    question_tense1 = 'have'
                    what_tense = 'has'
                else:
                    question_tense1 = 'has'
                    what_tense = 'has'
            else:
                if plural:
                    question_tense1 = 'do'
                else:
                    question_tense1 = 'does'
                verb_str = verb.lemma_

            # print(entity)
            if verb.text in why_dict:
                q = "Why " + question_tense1 + " " + subject + " " + verb_str + " " + object + "?"
                question_set.add(q)
            if verb.text in when_dict:
                question_status = False
                for modifier in verb_modifier:
                    for ner in when_dict[verb.text]:
                        if ner in modifier:
                            question_status = True
                            break
                if question_status:
                    q = "When " + question_tense1 + " " + subject + " " + verb_str + " " + object + "?"
                    question_set.add(q)
            if verb.text in where_dict:
                question_status = False
                for modifier in verb_modifier:
                    for ner in where_dict[verb.text]:
                        if ner in modifier:
                            question_status = True
                            break
                if question_status:
                    q = "Where " + question_tense1 + " " + subject + " " + verb_str + " " + object + "?"
                    question_set.add(q)

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

            start, end = len(sent),-1
            svo_end = max(sent.find(subject)+len(subject),sent.find(object)+len(object))
            for modifier in verb_modifier:
                idx = sent.find(' '.join(modifier.split(' ')[0:2]))
                if idx>=svo_end and idx<start:
                    start = idx
                if idx>=svo_end and idx+len(modifier)>end:
                    end = idx+len(modifier)

            modifier_sent = (""if len(verb_modifier) == 0 else " " + sent[start:end+1])
            if modifier_sent and modifier_sent[-1]=='.':
                modifier_sent = modifier_sent[:-1]

            q = question_type + " " + (""if what_tense == "" else what_tense + " ") + what_verb + ("" if object=="" or object==" " else " " + object) + modifier_sent + "?"
            print(q)
            question_set.add(q)
            if object!="" and object!=" ":
                q_obj = question_type + " " + question_tense1 + " " + subject + " " + verb_str  + modifier_sent + "?"
                print(q_obj)
                question_set.add(q_obj)


    # print(len(question_set))
    # print(question_set)
    return question_set


if __name__ == '__main__':
    # document_path = "../data/set1/a1.txt"
    # question_set = generate_questions(document_path)

    for s in range(1, 5):
        for a in range(1, 11):
            document_path = f"../data/set{s}/a{a}.txt"
            question_set = generate_questions(document_path)
            print(random.sample(question_set, 1), s, a)
