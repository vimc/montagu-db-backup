FROM ubuntu:24.04

# We need python for our scripts as well as for barman.  It's put
# first because this also downloads wget which we need to get the gpg
# key from the postgres deb repo
#
# For the "EXTERNALLY-MANAGED" bit, see:
# https://elliottback.medium.com/python-this-environment-is-externally-managed-error-and-docker-6062aac20a6e
RUN apt-get update && \
        apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        ca-certificates \
        git \
        gnupg2 \
        python3-dev \
        python3-pip \
        python3-setuptools \
        python3-wheel && \
        rm /usr/lib/python*/EXTERNALLY-MANAGED && \
        pip3 install \
        docopt \
        yacron

# Setting TZ here is necessary to stop apt interactively prompting for
# configuration options, followed by the environment variable
# DEBIAN_FRONTEND=noninteractive before the install itself.
ENV TZ=Europe/London
RUN install -d /usr/share/postgresql-common/pgdg && \
        curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc && \
        sh -c 'echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt noble-pgdg main" > /etc/apt/sources.list.d/pgdg.list' && \
        apt-get update && \
        DEBIAN_FRONTEND=noninteractive apt-get install -y \
                barman \
                postgresql-client-10

# This is a peculiar way of "installing" python packages that I do not
# have the energy to refactor right now.
ENV METRICS_UTILS_REF=4b2ef9b
RUN git clone https://github.com/vimc/metrics-utils /tmp/metrics_utils && \
        git -C /tmp/metrics_utils reset --hard $METRICS_UTILS_REF && \
        rm -rf /tmp/metrics_utils/.git && \
        mv /tmp/metrics_utils /usr/local/lib/python3.12/dist-packages

VOLUME /var/lib/barman
VOLUME /var/log/barman
VOLUME /recover
VOLUME /nightly
VOLUME /metrics

COPY etc /etc
COPY bin /usr/local/bin
COPY schedule.yml /schedule.yml

ENTRYPOINT ["barman-entrypoint"]
