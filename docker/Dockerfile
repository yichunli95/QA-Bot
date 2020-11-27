# Ubuntu Linux as the base image
FROM ubuntu:18.04

# Set UTF-8 encoding
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# Install Python
RUN apt-get -y update && \
    apt-get -y upgrade && \
	apt-get -y install python3-pip python3-dev

# Install spaCy
RUN pip3 install --upgrade pip
RUN pip3 install spacy
#RUN python3 -m spacy download en_core_web_lg
RUN python3 -m spacy download en_core_web_sm
RUN pip3 install nltk

# Install extra packages for answer program
RUN mkdir /QA
RUN pip3 install transformers
RUN pip3 install rank_bm25
RUN pip3 install pyinflect
RUN mkdir /QA/GloVe
RUN mkdir /QA/encoder
ADD GloVe /QA/GloVe
ADD encoder /QA/encoder
RUN python3 -m nltk.downloader punkt
RUN pip3 install torch torchvision
RUN pip3 install sklearn
RUN pip3 install numpy

# Add the files into container, under QA folder, modify this based on your need
ADD ask /QA
ADD answer /QA
RUN mkdir /QA/ask_engine
RUN mkdir /QA/ans_engine
ADD ask_engine /QA/ask_engine
ADD ans_engine /QA/ans_engine

# Change the permissions of programs
CMD ["chmod 777 /QA/*"]

# Set working dir as /QA
WORKDIR /QA
ENTRYPOINT ["/bin/bash", "-c"]
