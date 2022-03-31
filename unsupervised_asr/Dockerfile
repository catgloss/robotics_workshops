# Dockerfile for building PyKaldi image from Ubuntu 18.04 image
FROM nvidia/cuda:11.0-cudnn8-devel-ubuntu18.04
#FROM ubuntu:18.04

#############################################################################
#              Install necessary system packages                            #
#############################################################################
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    build-essential \
    ca-certificates \
    vim \
    nano \
    htop \
    zsh \
    #for pykaldi 
    python3 python3-pip python3-dev \
    python3-venv \
    python2.7 \
    autoconf \
    automake \
    cmake \
    curl \
    g++ \
    git \
    graphviz \
    libatlas3-base \
    libtool \
    make \
    pkg-config \
    sox \
    subversion \
    unzip \
    wget \
    zlib1g-dev \
    espeak \
    espeak-ng \
    # for MKL
    apt-transport-https gpg-agent gnupg2 \
    cpio \ 
    # for kenlm
    libboost-thread-dev libboost-test-dev libboost-system-dev libboost-program-options-dev \
    # FFTW
    libfftw3-dev \
    # ssh for OpenMPI
    openssh-server openssh-client \
    # for OpenMPI
    libopenmpi-dev openmpi-bin \
    # for kenlm
    zlib1g-dev libbz2-dev liblzma-dev \
    #for kaldi
    gfortran \
    libomp-dev \
    # OpenBLAS
    libopenblas-dev liblapacke-dev \
    # for glog
    libgoogle-glog-dev libgoogle-glog0v5 \
    # python sox
    sox libsox-dev \ 
    #for faiss
    python3-setuptools \
    && \
    # Make python3 default
    ln -s /usr/bin/python3 /usr/bin/python \
    && ln -s /usr/bin/pip3 /usr/bin/pip

#############################################################################
#                                Python Packages                            #
#############################################################################
 
COPY ./requirements.txt /unsupervised/
RUN pip install --upgrade pip && \
    pip install -r /unsupervised/requirements.txt

#############################################################################
#                                DEPENDENCIES                               #
#############################################################################
# fasttext language identification
RUN cd /opt && mkdir fasttext && cd fasttext && \
    wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin

#rVAD
RUN cd /opt && git clone https://github.com/zhenghuatan/rVADfast.git
ENV RVAD_ROOT="/opt/rVADfast/"

#Kenlm
RUN cd /tmp && git clone https://github.com/kpu/kenlm.git && \
    cd kenlm && git checkout 0c4dd4e && \
    mkdir build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release \
             -DCMAKE_INSTALL_PREFIX=/opt/kenlm \
             -DCMAKE_POSITION_INDEPENDENT_CODE=ON && \
    make install -j$(nproc)

ENV CMAKE_INCLUDE_PATH="/opt/kenlm:${CMAKE_INCLUDE_PATH}"
ENV KENLM_ROOT="/opt/kenlm"  
ENV KENLM_LIB="/opt/kenlm/build/lib/libkenlm.a"
ENV KENLM_UTIL_LIB="/opt/kenlm/build/lib/libkenlm_util.a"
#clean up
RUN apt-get clean && \
    apt-get -y autoremove && \
    rm -rf /var/lib/apt/lists/*

#MKL
ENV APT_INSTALL="apt-get install -y --no-install-recommends"


RUN cd /tmp && wget https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
    apt-key add GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
    sh -c 'echo deb https://apt.repos.intel.com/mkl all main > /etc/apt/sources.list.d/intel-mkl.list' && \
    apt-get update && DEBIAN_FRONTEND=noninteractive $APT_INSTALL intel-mkl-64bit-2020.4-912

ENV MKLROOT="/opt/intel/mkl"


#Flashlight python binding with cuda
RUN cd /opt && git clone https://github.com/flashlight/flashlight.git && \
    cd flashlight/bindings/python && python setup.py install

#Flashlight python binding without cuda!!!
#RUN export USE_CUDA=0 && \
#    cd /tmp && git clone https://github.com/flashlight/flashlight.git && \
#    cd flashlight/bindings/python && python setup.py install

#pykaldi
RUN cd /opt && git clone https://github.com/pykaldi/pykaldi.git && \
    cd pykaldi/tools \
    && ./check_dependencies.sh \
    && ./install_protobuf.sh \
    && ./install_clif.sh \
    && ./install_kaldi.sh \
    && cd .. \
    && python setup.py install \
    && rm -rf tools/clif_backend \
    && rm -rf tools/protobuf
ENV KALDI_ROOT="/opt/pykaldi/tools/kaldi"


#Fairseq
RUN cd / && git clone https://github.com/mahshidaln/fairseq.git && \
    cd fairseq && \
    pip install --editable ./
ENV FAIRSEQ_ROOT="/fairseq"