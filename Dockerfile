FROM ubuntu:16.04

# We need python for our scripts as well as for barman.  It's put
# first because this also downloads wget which we need to get the gpg
# key from the postgres deb repo
RUN apt-get update && \
        apt-get install -y --no-install-recommends \
                cron \
                python-flask \
                python3-pip \
                python3-setuptools \
                wget

RUN pip3 install docopt

RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | \
        apt-key add - && \
        sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main" >> /etc/apt/sources.list.d/postgresql.list' && \
        apt-get update && \
        apt-get install -y \
                barman \
                postgresql-client-10

VOLUME /var/lib/barman
VOLUME /var/log/barman
VOLUME /recover
VOLUME /nightly

COPY etc /etc
COPY bin /usr/local/bin

WORKDIR /app
COPY metrics/bin/requirements.txt .
RUN pip3 install -r requirements.txt
COPY metrics/bin/montagu_metrics/requirements.txt montagu_metrics/requirements.txt
RUN pip3 install -r montagu_metrics/requirements.txt

COPY metrics /app
ENV FLASK_APP=main.py
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ENTRYPOINT ["flask", "run", "--host=0.0.0.0"]
