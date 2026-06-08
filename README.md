
# MLOps - Batch Signal Pipeline

## Overview
A simple MLOps-style batch pipeline that:
- Loads config from YAML
- Reads OHLCV CSV data
- Uses only the `close` column
- Computes rolling mean (config-based window)
- Generates a binary signal (close > rolling mean)
- Outputs metrics + logs

---

## Input Format

### config.yaml
```yaml
seed: 42
window: 5
version: "v1"
````

### data.csv

Must contain a `close` column.

---

## How to run (Local)

```bash id="runlocal"
pip install -r requirements.txt

python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```

---

## How to run (Docker)

```bash id="rundocker"
docker build -t mlops-task .

docker run --rm mlops-task
```

---

## Output

* `metrics.json` → final metrics
* `run.log` → execution logs
* stdout → summary JSON

---

## Notes

* Fully reproducible (fixed seed)
* Config-driven pipeline
* No hardcoded paths
* Works locally + Docker

```

