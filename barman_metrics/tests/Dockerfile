FROM python:3

WORKDIR /app

COPY ./backup/barman_metrics/bin/requirements-dev.txt /app/
COPY ./backup/barman_metrics/bin/requirements.txt /app/
RUN pip3 install -r requirements.txt
RUN pip3 install -r requirements-dev.txt

COPY ./backup/barman_metrics/bin /app/bin
COPY ./backup/barman_metrics/tests /app/tests

ENTRYPOINT ["pytest", "--teamcity"]
