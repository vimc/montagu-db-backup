FROM ubuntu:18.04

# We need python for our scripts as well as for barman.  It's put
# first because this also downloads wget which we need to get the gpg
# key from the postgres deb repo
RUN apt-get update && \
        apt-get install -y --no-install-recommends \
                git \
                python3-pip \
                python3-setuptools \
                wget

RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | \
        apt-key add - && \
        sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main" >> /etc/apt/sources.list.d/postgresql.list' && \
        apt-get update && \
        apt-get install -y \
                barman \
                postgresql-client-10

RUN pip3 install \
        docopt \
        yacron

ENV METRICS_UTILS_REF 4b2ef9b
RUN git clone https://github.com/vimc/metrics-utils /tmp/metrics_utils && \
        git -C /tmp/metrics_utils reset --hard $METRICS_UTILS_REF && \
        pip3 install -r /tmp/metrics_utils/requirements.txt && \
        rm -rf /tmp/metrics_utils/.git && \
        mv /tmp/metrics_utils /usr/local/lib/python3.5/dist-packages

VOLUME /var/lib/barman
VOLUME /var/log/barman
VOLUME /recover
VOLUME /nightly
VOLUME /metrics

COPY etc /etc
COPY bin /usr/local/bin
COPY schedule.yml /schedule.yml

ENTRYPOINT ["barman-entrypoint"]
