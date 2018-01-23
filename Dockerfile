# It's not totally obvious if it's better here to base this off of
# postgres:9.6 or off of ubuntu.
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

COPY barman.conf /etc/barman.conf
COPY montagu.conf /etc/barman.d/montagu.conf
COPY bin /usr/local/bin

VOLUME /var/lib/barman

ENTRYPOINT ["bash"]
