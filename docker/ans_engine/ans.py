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
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import warnings
# def open_document(file_path):
#     with io.open(file_path, 'r', encoding='utf8') as f:
#         document = f.read()
#     document = re.sub('[\n]+', ' . ', document)
#     return document

def answer(input_file, question_file):
    # Initialize Model
    warnings.filterwarnings("ignore", category=UserWarning)
    V = 1
    MODEL_PATH = 'encoder/infersent%s.pkl' % V
    params_model = {'bsize': 64, 'word_emb_dim': 300, 'enc_lstm_dim': 2048,
                    'pool_type': 'max', 'dpout_model': 0.0, 'version': V}
    infersent = answer_model.InferSent(params_model)
    infersent.load_state_dict(torch.load(MODEL_PATH, map_location='cpu'))
    #infersent.load_state_dict(torch.load(MODEL_PATH))

    infersent.set_w2v_path("GloVe/glove.840B.300d.txt")

    # Load pre-trained, fine-tuned models
    #print("p a")
    #tokenizer = AutoTokenizer.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
    #model = AutoModelForQuestionAnswering.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")

    # path relative to the answer program (not sure why tho)
    # large model (need Gb+ memory during runtime)
    tokenizer = AutoTokenizer.from_pretrained("./ans_engine/bert_large_model")
    model = AutoModelForQuestionAnswering.from_pretrained("./ans_engine/bert_large_model")

    # small model 
    # tokenizer = AutoTokenizer.from_pretrained("./ans_engine/bert_small_model")
    # model = AutoModelForQuestionAnswering.from_pretrained("./ans_engine/bert_small_model")
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
    # questions = open_document(question_file)
    #print(questions)
    sentences_embedding = infersent.encode(sentences, tokenize = True)
    tokenized_sentences = [s.split(" ") for s in sentences]
    bm25 = BM25Okapi(tokenized_sentences)


    # Answer questions
    #answers = []
    #print(questions)
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
        #print('*'*100)
        #print(score)
        #print('Question:\n', question)
        context = ''
        for ct, k in enumerate(score.keys()):
            if ct == 3: #choose top ct candidate answer-sentences
                break
            context += sentences[k]
            # print('*'*100)
            # print(sentences[k])
        #print('Context:\n', context)

        #inputs = tokenizer.encode_plus(question, context, return_tensors="pt").to(args.device)
        inputs = tokenizer.encode_plus(question, context, return_tensors="pt")
        for k in inputs:
            inputs[k] = torch.unsqueeze(inputs[k][0][:512],0)

        answer_start_scores, answer_end_scores = model(**inputs)
        answer_starts = torch.argsort(answer_start_scores, descending=True)[0][0:5]
        answer_ends = torch.argsort(answer_end_scores, descending=True)[0][0:5]

        #print('Answer(s):')

        for i in range(len(answer_starts)):
            if i == 1:
                break
            answer_start = answer_starts[i]
            answer_end = answer_ends[i] + 1  
            #print("======")
            print(tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end])))
