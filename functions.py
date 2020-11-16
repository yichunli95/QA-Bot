#!/usr/bin/env python3
import io
import nltk
import re
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
    # sentences = sentences[0:4]
    who_key_word = ['he', 'she', 'they', 'him', 'her', 'them', 'who']

    for sent in sentences:
        # sent = "Although much of their artistic effort was centered on preserving life after death, Egyptians also surrounded themselves with objects to enhance their lives in this world, producing elegant jewelry, finely carved and inlaid furniture, and cosmetic vessels and implements made from a wide range of materials."
        token = nlp(sent)
        # print("Sentence: ", token)
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

        result = findSVOs(token)
        # print("why: ", why_dict)
        # print("when: ", when_dict)
        # print("where: ", where_dict)
        # print("svo:", result)
        # print("Questions:")
        for entity in result:
            subject, subject_tag, negation, verb, object, verb_modifier = entity
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
                    what_tense = 'have'
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
                print("Why " + question_tense1 + " " + subject + " " + verb_str + " " + object + "?")
            if verb.text in when_dict:
                question_status = False
                for modifier in verb_modifier:
                    for ner in when_dict[verb.text]:
                        if ner in modifier:
                            question_status = True
                            break
                if question_status:
                    print("When " + question_tense1 + " " + subject + " " + verb_str + " " + object + "?")
            if verb.text in where_dict:
                question_status = False
                for modifier in verb_modifier:
                    for ner in where_dict[verb.text]:
                        if ner in modifier:
                            question_status = True
                            break
                if question_status:
                    print("Where " + question_tense1 + " " + subject + " " + verb_str + " " + object + "?")

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
            print(question_type + " " + ("" if what_tense == "" else what_tense + " ") + what_verb + " " + object + "?")
            print(subject)

