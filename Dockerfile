FROM ubuntu:16.04

RUN apt-get update && \
        apt-get install -y wget

RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | \
        apt-key add - && \
        sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main" >> /etc/apt/sources.list.d/postgresql.list' && \
        apt-get update && \
        apt-get install -y \
                barman \
                postgresql-client-9.6

VOLUME /var/lib/barman

COPY etc /etc
COPY bin /usr/local/bin

ENTRYPOINT ["idle"]
