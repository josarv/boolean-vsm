FROM python:3.12-slim

WORKDIR /ir

COPY requirements.txt ./

RUN apt-get update && apt-get install --no-install-recommends -y default-jre

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

# when project ready, add a COPY instruction, and an appropriate dockerignore
