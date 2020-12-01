#!/usr/bin/python3 -W ignore
# -*- coding:utf8 -*-

import os
#from answer_model import InferSent
import nltk
import torch
from . import answer_model
import codecs
import re
from sklearn.metrics.pairwise import cosine_similarity
from sklearn import preprocessing
from rank_bm25 import BM25Okapi
import numpy as np
from transformers import AutoTokenizer, AutoModelForQuestionAnswering, AutoModelForSequenceClassification
import warnings
import spacy


def answer(input_file, question_file):
    # Initialize Model
    cuda = torch.cuda.is_available()
    device = torch.device("cuda" if cuda else "cpu")

    warnings.filterwarnings("ignore", category=UserWarning)
    V = 1
    MODEL_PATH = 'encoder/infersent%s.pkl' % V
    params_model = {'bsize': 64, 'word_emb_dim': 300, 'enc_lstm_dim': 2048,
                    'pool_type': 'max', 'dpout_model': 0.0, 'version': V}
    infersent = answer_model.InferSent(params_model)
    infersent.load_state_dict(torch.load(MODEL_PATH, map_location='cpu'))
    #infersent.load_state_dict(torch.load(MODEL_PATH))

    infersent.set_w2v_path("GloVe/glove.840B.300d.txt")


    # path relative to the answer program (not sure why tho)
    # large model (need Gb+ memory during runtime)
    wh_tokenizer = AutoTokenizer.from_pretrained("./ans_engine/wh_model")
    wh_model = AutoModelForQuestionAnswering.from_pretrained("./ans_engine/wh_model").to(device)

    boolean_tokenizer = AutoTokenizer.from_pretrained("./ans_engine/boolean_model")
    boolean_model = AutoModelForSequenceClassification.from_pretrained("./ans_engine/boolean_model").to(device)

    sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    # load test file
    text = codecs.open(input_file,'r','utf-8').read()
    #text = open_document(input_file)
    text = re.sub('\n+', '. ', text)
    sentences = sentence_tokenizer.tokenize(text)

    # setup measures
    score = {} # {idx: (BM25, InferSent) }
    # InferSent for sentence semantic similarity
    infersent.build_vocab(sentences, tokenize=True)

    with open(question_file,'r') as f:
        questions = f.readlines()
    sentences_embedding = infersent.encode(sentences, tokenize = True)
    tokenized_sentences = [s.split(" ") for s in sentences]
    bm25 = BM25Okapi(tokenized_sentences)

    for question in questions:
        question_embedding = infersent.encode([question],tokenize = True)[0]
        tokenized_question = question.split(" ")
        # BM25 scores
        bm_scores = preprocessing.normalize(bm25.get_scores(tokenized_question).reshape(1,-1), norm = 'l1')[0]
        # print(bm_scores)

        # Infersent mathcing scores
        infersent_scores = []
        for idx,s in enumerate(sentences_embedding):
            infersent_scores.append(cosine_similarity(question_embedding.reshape(1,-1), s.reshape(1,-1))[0][0])
        infersent_scores = preprocessing.normalize(np.array(infersent_scores).reshape(1,-1), norm = 'l1')[0]
        # print(infersent_scores)

        for idx in range(len(bm_scores)):
            score[idx] = (bm_scores[idx], infersent_scores[idx])

        score = {k: v for k, v in sorted(score.items(), reverse=True, key=lambda item: item[1][0]+item[1][1])}
        # print('*'*100)
        # print(score)
        # print('Question:\n', question)
        context = ''
        for ct, k in enumerate(score.keys()):
            if ct == 3: #choose top ct candidate answer-sentences
                break
            context += sentences[k]
            # print('*'*100)
            # print(sentences[k])
        #print('Context:\n', context)


        if is_binary_question(question):
            sequence = boolean_tokenizer.encode_plus(question, context, return_tensors="pt")['input_ids'].to(device)
            #logits = boolean_model(sequence)[0]
            #print(boolean_model(sequence))
            logits = boolean_model(sequence).logits
            probabilities = torch.softmax(logits, dim=1).detach().cpu().tolist()[0]
            proba_yes = round(probabilities[1], 2)
            proba_no = round(probabilities[0], 2)
            if proba_yes >= proba_no:
                print("Yes.")
            else:
                print("No.")
            #print(f"Yes: {proba_yes}", f"No: {proba_no}")
        else:
            inputs = wh_tokenizer.encode_plus(question, context, return_tensors="pt").to(device)
            for k in inputs:
                inputs[k] = torch.unsqueeze(inputs[k][0][:512],0)
            #answer_start_scores, answer_end_scores = wh_model(**inputs)
            output = wh_model(**inputs)
            answer_start_scores, answer_end_scores = output.start_logits, output.end_logits
            #print(wh_model(**inputs))
            #print(answer_start_scores)
            answer_starts = torch.argsort(answer_start_scores, descending=True)[0][0:5]
            answer_ends = torch.argsort(answer_end_scores, descending=True)[0][0:5]

            #print('Answer(s):')
            for i in range(len(answer_starts)):
                if i == 1:
                    break
                answer_start = answer_starts[i]
                answer_end = answer_ends[i] + 1  
                answer = wh_tokenizer.convert_tokens_to_string(wh_tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end]))
                answer = answer.capitalize() + "."
                print(answer)







# funcs for determining whether a question is boolean or not
def find_root(sent, return_idx = True):
    for idx,word in enumerate(sent):
        if word.head == word:
            if return_idx:
                return word, idx
            else:
                return word

def is_binary_question(question):
    wh = {'how', 'what', 'when', 'where', 'which', 'who', 'whom', 'why', 'whose'}
    tf = {'is','are','do','does','was','were','did','have','has','would','will', 'whether','should','must', 'can', 'could', 'would', 'shall'}
    # Segment question sentence into clause(s)
    nlp = spacy.load("en_core_web_sm")
    sent = nlp(question)
    
    # displacy.render(sent, style='dep', jupyter=True, options={'distance': 90})
    if ',' in sent.text:
        root, root_idx = find_root(sent)
        # print('root:',root, root_idx)
        l = max(root_idx - 1, 0)
        r = min(root_idx + 1, len(sent))
        while l > 0:
            if sent[l].text == ',':
                l += 1
                break
            l -= 1
        while r < len(sent):
            if sent[r].text == ',':
                break
            r += 1
        sent = list(sent.__iter__())[l:r]
    
    ct = 1
    wh_idx = None
    tf_idx = None
    for word in sent:
        if word.text.lower() in wh and not wh_idx:
            wh_idx = ct
        if ((word.text.lower() in tf) or word.dep_ == 'aux') and not tf_idx:
            tf_idx = ct
        ct += 1

    if tf_idx and not wh_idx:
        return True
    if not tf_idx and wh_idx:
        return False
    if tf_idx and wh_idx:
        if tf_idx < wh_idx:
            return True
        else:
            return False