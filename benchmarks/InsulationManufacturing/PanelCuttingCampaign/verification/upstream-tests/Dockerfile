FROM python:3.12.14-slim-trixie@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f
RUN sed -i 's|http://deb.debian.org|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources && apt-get update && apt-get install -y --no-install-recommends g++ && rm -rf /var/lib/apt/lists/*
WORKDIR /tests
COPY . /tests
RUN g++ -std=c++14 -O2 -Iupstream-checker/include upstream-checker/src/*.cpp -o /tests/checker && dpkg-query -W > /opt/dependency-versions.txt
