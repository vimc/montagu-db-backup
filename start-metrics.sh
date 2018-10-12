#!/usr/bin/env bash
set -ex

cat <<EOF > config.json
{
  "labels": {
    "db_name": "montagu"
  },
  "cache_volume": "barman_metrics",
  "cache_filename": "metrics.json",
  "port": 5000,
  "name": "barman-metrics",
  "max_age_seconds": 600
}
EOF

./cached-metrics/scripts/run --public