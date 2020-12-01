# Ubuntu Linux as the base image
FROM nvidia/cuda:10.2-base-ubuntu18.04

# Set UTF-8 encoding
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# Install some basic utilities
# RUN apt-get update && apt-get install -y \
#     curl \
#     ca-certificates \
#     sudo \
#     git \
#     bzip2 \
#     libx11-6 \
#  && rm -rf /var/lib/apt/lists/*
RUN apt-get -y update && \
    apt-get -y upgrade && \
	apt-get -y install python3-pip python3-dev

# RUN mkdir /app
# WORKDIR /app
# Install Miniconda and Python 3.8
# ENV CONDA_AUTO_UPDATE_CONDA=false
# ENV PATH=/root/miniconda/bin:$PATH
# RUN curl -sLo ~/miniconda.sh https://repo.continuum.io/miniconda/Miniconda3-py38_4.8.2-Linux-x86_64.sh \
#  && chmod +x ~/miniconda.sh \
#  && ~/miniconda.sh -b -p ~/miniconda \
#  && rm ~/miniconda.sh \
#  && conda install -y python==3.8.1 \
#  && conda clean -ya

# RUN conda install -y -c pytorch \
#     cudatoolkit=10.2 \
#     "pytorch=1.5.0=py3.8_cuda10.2.89_cudnn7.6.5_0" \
#     "torchvision=0.6.0=py38_cu102" \
#  && conda clean -ya

# Install stuff with conda
RUN pip3 install --upgrade pip
RUN pip3 install numpy
RUN pip3 install spacy
RUN python3 -m spacy download en_core_web_sm
RUN pip3 install nltk
RUN python3 -m nltk.downloader punkt

RUN pip3 install torch torchvision
RUN pip3 install sklearn
RUN pip3 install transformers
RUN pip3 install rank_bm25
RUN pip3 install pyinflect

# Install extra packages for answer program
RUN mkdir /QA
RUN mkdir /QA/GloVe
RUN mkdir /QA/encoder
ADD GloVe /QA/GloVe
ADD encoder /QA/encoder

# Add the files into container, under QA folder, modify this based on your need
ADD ask /QA
ADD answer /QA
RUN mkdir /QA/ask_engine
RUN mkdir /QA/ans_engine
ADD ask_engine /QA/ask_engine
ADD ans_engine /QA/ans_engine

# # Create a non-root user and switch to it
# RUN adduser --disabled-password --gecos '' --shell /bin/bash user \
#  && chown -R user:user /app
# RUN echo "user ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-user
# USER user

# # All users can use /home/user as their home directory
# ENV HOME=/home/user
# RUN chmod 777 /home/user



# Change the permissions of programs
CMD ["chmod 777 /QA/*"]

# Set working dir as /QA
WORKDIR /QA
ENTRYPOINT ["/bin/bash", "-c"]
