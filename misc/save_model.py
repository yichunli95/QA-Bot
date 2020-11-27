from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import os

def save_model():
    #tokenizer = AutoTokenizer.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
    #model = AutoModelForQuestionAnswering.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
    # tokenizer = AutoTokenizer.from_pretrained("distilbert-base-cased-distilled-squad")
    # model = AutoModelForQuestionAnswering.from_pretrained("distilbert-base-cased-distilled-squad")
    # tokenizer.save_pretrained("/Users/yichunli/Desktop/agares-nlp/docker/ans_engine/wh_model")
    # model.save_pretrained("/Users/yichunli/Desktop/agares-nlp/docker/ans_engine/wh_model")
    tokenizer = AutoTokenizer.from_pretrained("roberta-large") 
    tokenizer.save_pretrained("/Users/yichunli/Desktop/agares-nlp/docker/ans_engine/boolean_model")


if __name__ == '__main__':
    save_model()