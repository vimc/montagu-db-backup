FROM ubuntu:24.04

ENV TZ=Europe/London

# We need python for our scripts as well as for barman.  It's put
# first because this also downloads wget which we need to get the gpg
# key from the postgres deb repo
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    git \
    gnupg2 \
    postgresql-common \
    python3-dev \
    python3-docopt \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    wget

RUN /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y && \
    apt-get install -y --no-install-recommends \
    barman \
    postgresql-client-17

RUN pipx install yacron

# This will require some attention.
# ENV METRICS_UTILS_REF=4b2ef9b
# RUN git clone https://github.com/vimc/metrics-utils /tmp/metrics_utils && \
#         git -C /tmp/metrics_utils reset --hard $METRICS_UTILS_REF && \
#         pip3 install -r /tmp/metrics_utils/requirements.txt && \
#         rm -rf /tmp/metrics_utils/.git && \
#         mv /tmp/metrics_utils /usr/local/lib/python3.6/dist-packages

VOLUME /var/lib/barman
VOLUME /var/log/barman
VOLUME /recover
VOLUME /nightly
VOLUME /metrics

COPY etc /etc
COPY bin /usr/local/bin
COPY schedule.yml /schedule.yml

ENTRYPOINT ["barman-entrypoint"]
