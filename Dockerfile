FROM python:3 AS base
RUN apt-get update && apt-get install -y poppler-utils pandoc
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS app
WORKDIR /usr/src/app
COPY . .
RUN pip install -e .
RUN pytest
CMD ["search"]