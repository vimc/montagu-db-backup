FROM ubuntu:16.04

ENV BARMAN_START=/var/run/barman_start

RUN apt-get update && \
        apt-get install -y wget

RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | \
        apt-key add - && \
        sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main" >> /etc/apt/sources.list.d/postgresql.list' && \
        apt-get update && \
        apt-get install -y \
                barman \
                postgresql-client-9.6

COPY etc /etc
COPY bin /usr/local/bin

VOLUME /var/lib/barman

ENTRYPOINT ["entrypoint_barman"]
