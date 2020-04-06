# https://lucene.apache.org/pylucene/install.html
# https://github.com/coady/docker/blob/master/pylucene/Dockerfile
FROM coady/pylucene:7 as pyenv
RUN apt-get update && apt-get install -y poppler-utils pandoc
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