FROM python:3

WORKDIR /app

COPY ./backup/metrics/app/requirements-dev.txt /app/
COPY ./backup/metrics/app/requirements.txt /app/
RUN pip3 install -r requirements.txt
RUN pip3 install -r requirements-dev.txt

COPY ./backup/metrics/app /app/app
COPY ./backup/metrics/tests /app/tests

ENTRYPOINT ["pytest", "--teamcity"]
