#!/usr/bin/env bash
docker build -f ./backup/metrics/tests/Dockerfile --tag barman_metrics_tests .
docker run --rm \
    barman_metrics_tests
