#!/usr/bin/python3 -W ignore::DeprecationWarning
# -*- coding:utf8 -*-
#/usr/bin/env python3

#!/usr/bin/env python3

import io
import nltk
import re
import spacy
import random
import pyinflect

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

def format_subject(ner_dict, subject):
    subject_formatted = subject.split(' ')
    subject_formatted[0] = subject_formatted[0].lower()
    subject_formatted = subject if subject_formatted[0] in ner_dict.keys() else ' '.join(subject_formatted)
    return subject_formatted

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


def generate_question_modifier(sent, subject, object, verb_modifier, exception_list):
    # generate question modifier
    start, end = len(sent), -1
    svo_end = max(sent.find(subject) + len(subject), sent.find(object) + len(object))
    for modifier in verb_modifier:
        if modifier in exception_list:
            continue
        idx = sent.find(' '.join(modifier.split(' ')[0:2]))
        if svo_end <= idx < start:
            start = idx
        if idx >= svo_end and idx + len(modifier) > end:
            end = idx + len(modifier)

    modifier_sent = sent[start:end + 1].strip()
    if modifier_sent != "":
        modifier_sent = " " + modifier_sent
    if modifier_sent and (modifier_sent[-1] == '.' or modifier_sent[-1] == ','):
        modifier_sent = modifier_sent[:-1]

    return modifier_sent


def generate_questions(document_path):
    document = open_document(document_path)
    sentences = tokenize_sentence(document)
    # sentences = sentences[0:10]
    who_key_word = ['he', 'she', 'they', 'him', 'her', 'them', 'who']
    question_set = set()
    question_length_limit = 30

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
            subject_formatted = format_subject(ner_dict, subject)
            object_formatted = format_subject(ner_dict, object)
            # if negation!="":
            #     print(entity)
            print(entity)
            # generate question about verb
            question_tense1 = ''
            what_tense = ''
            tense = verb.tag_
            print(tense)
            plural = subject_tag == 'NNS' or subject_tag == 'NNPS'

            verb_str = verb.text
            what_verb = verb.text
            if tense == 'VBD':
                question_tense1 = 'did'
                verb_str = verb.lemma_
                if subject == " ":
                    question_tense1 = 'was'
            elif tense == 'VBG':
                if plural:
                    question_tense1 = 'are'
                    what_tense = 'are'
                else:
                    question_tense1 = 'is'
                    what_tense = 'is'
                if subject == " ":
                    question_tense1 = 'is'
            elif tense == 'VBN':
                if plural:
                    question_tense1 = 'have'
                    what_tense = 'has'
                else:
                    question_tense1 = 'has'
                    what_tense = 'has'
                if subject == " ":
                    question_tense1 = 'is'
            else:
                if plural:
                    question_tense1 = 'do'
                else:
                    question_tense1 = 'does'
                verb_str = verb.lemma_
                if subject == " ":
                    question_tense1 = 'is'
            if subject == " ":
                verb_str = verb._.inflect('VBN')

            # generate why question
            if verb.text in why_dict:
                why_key_word = ['because']
                exception_list = []
                for modifier in verb_modifier:
                    for key_word in why_key_word:
                        if key_word in modifier:
                            exception_list.append(modifier)
                modifier_sent = generate_question_modifier(sent, subject, object, verb_modifier, exception_list)
                if subject != " ":
                    q = "Why " + question_tense1 + " " + subject_formatted + " " + verb_str + ("" if object_formatted == " " else " " + object_formatted) + modifier_sent + "?"
                    if len(q)>=question_length_limit:
                        print(q)
                        question_set.add(q)

            # generate when question
            if verb.text in when_dict:
                exception_list = []
                question_status = False
                for modifier in verb_modifier:
                    for ner in when_dict[verb.text]:
                        if ner in modifier:
                            question_status = True
                            exception_list.append(modifier)
                if question_status:
                    modifier_sent = generate_question_modifier(sent, subject, object, verb_modifier, exception_list)
                    if subject != " ":
                        q = "When " + question_tense1 + " " + subject_formatted + " " + verb_str + ("" if object_formatted == " " else " " + object_formatted) + modifier_sent + "?"
                        if len(q) >= question_length_limit:
                            print(q)
                            question_set.add(q)

            # generate where question
            if verb.text in where_dict:
                exception_list = []
                question_status = False
                for modifier in verb_modifier:
                    for ner in where_dict[verb.text]:
                        if ner in modifier:
                            question_status = True
                            exception_list.append(modifier)
                if question_status:
                    modifier_sent = generate_question_modifier(sent, subject, object, verb_modifier, exception_list)
                    if subject != " ":
                        q = "Where " + question_tense1 + " " + subject_formatted + " " + verb_str + ("" if object_formatted == " " else " " + object_formatted) + modifier_sent + "?"
                        if len(q) >= question_length_limit:
                            print(q)
                            question_set.add(q)

            modifier_sent = generate_question_modifier(sent, subject, object, verb_modifier, [])

            # generate question about subject
            if subject != " ":
                question_type = "What"
                for k, v in ner_dict.items():
                    if k in subject.lower() and v == 'PERSON':
                        question_type = "Who"
                        break

                for key in who_key_word:
                    if subject.lower() == key:
                        question_type = "Who"
                        break

                q = question_type + " " + ("" if what_tense == "" else what_tense + " ") + what_verb + (
                    "" if object_formatted == " " else " " + object_formatted) + modifier_sent + "?"
                if len(q) >= question_length_limit:
                    print(q)
                    question_set.add(q)

            # generate question about object
            if object != " ":
                question_type = "What"
                for k, v in ner_dict.items():
                    if k in object.lower() and v == 'PERSON':
                        question_type = "Who"
                        break

                for key in who_key_word:
                    if object.lower() == key:
                        question_type = "Who"
                        break


                q_obj = question_type + " " + question_tense1 + (
                    "" if subject_formatted == " " else " " + subject_formatted) + " " + verb_str + modifier_sent + "?"
                if len(q_obj) >= question_length_limit:
                    print(q_obj)
                    question_set.add(q_obj)

            # generate T/F questions


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
