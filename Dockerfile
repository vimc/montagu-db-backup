FROM ubuntu:16.04

# We need python for our scripts as well as for barman.  It's put
# first because this also downloads wget which we need to get the gpg
# key from the postgres deb repo
RUN apt-get update && \
        apt-get install -y --no-install-recommends \
                python3-pip \
                python3-setuptools \
                wget

RUN pip3 install --upgrade pip &&\
        pip3 install docopt

RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | \
        apt-key add - && \
        sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main" >> /etc/apt/sources.list.d/postgresql.list' && \
        apt-get update && \
        apt-get install -y \
                barman \
                postgresql-client-10

VOLUME /var/lib/barman
VOLUME /var/log/barman
VOLUME /restore

COPY etc /etc
COPY bin /usr/local/bin

ENTRYPOINT ["idle"]
