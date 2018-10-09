FROM python:3

WORKDIR /app

COPY ./backup/metrics/bin/requirements-dev.txt /app/
COPY ./backup/metrics/bin/requirements.txt /app/
RUN pip3 install -r requirements.txt
RUN pip3 install -r requirements-dev.txt

COPY ./backup/metrics/bin /app/bin
COPY ./backup/metrics/tests /app/tests

ENTRYPOINT ["pytest", "--teamcity"]
