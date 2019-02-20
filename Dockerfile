FROM python:3 AS base
RUN apt-get update && apt-get install -y poppler-utils pandoc default-jdk ant
WORKDIR /usr/src/lucene
# https://lucene.apache.org/pylucene/install.html
# https://github.com/coady/docker/blob/master/pylucene/Dockerfile
RUN curl https://www.apache.org/dist/lucene/pylucene/pylucene-7.6.0-src.tar.gz | tar -xz --strip-components=1
RUN cd jcc && JCC_JDK=/usr/lib/jvm/default-java python setup.py install
RUN make all install JCC='python -m jcc' ANT=ant PYTHON=python NUM_FILES=8

FROM base as pyenv
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM pyenv AS app
WORKDIR /usr/src/app
COPY . .
RUN pip install -e .
RUN pytest
RUN mkdir /data
WORKDIR /data
CMD ["sift"]