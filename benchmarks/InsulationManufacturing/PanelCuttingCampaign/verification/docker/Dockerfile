FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends g++ libboost-program-options-dev make && rm -rf /var/lib/apt/lists/*
WORKDIR /task
COPY . /task
