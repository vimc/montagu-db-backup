# montagu-metrics-py
Helper functions for creating metric exporters for Prometheus.

Use like so:

1. Add the submodule at some local path, let's say `metrics`
   ```
   git submodule add https://github.com/vimc/montagu-metrics-py metrics
   ```
2. Add to your build/whatever script:
   ```
   pip3 install -r metrics/requirements.txt
   ```
3. Import and use:
   ```
   from metrics.metrics import render_metrics

   ```
