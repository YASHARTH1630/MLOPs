import argparse
import yaml
import pandas as pd
import numpy as np
import json
import logging
import time
import sys
from datetime import datetime


# ---------------- Logging Setup ----------------
def setup_logger(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger()


# ---------------- Load Config ----------------
def load_config(path, logger):
    try:
        with open(path, "r") as f:
            config = yaml.safe_load(f)

        required = ["seed", "window", "version"]
        for r in required:
            if r not in config:
                raise ValueError(f"Missing config field: {r}")

        logger.info("Config loaded and validated")
        return config

    except Exception as e:
        raise ValueError(f"Config error: {str(e)}")


# ---------------- Load Data ----------------
def load_data(path, logger):
    try:
        df = pd.read_csv(path)

        if df.empty:
            raise ValueError("CSV is empty")

        if "close" not in df.columns:
            raise ValueError("Missing required column: close")

        logger.info(f"Data loaded with {len(df)} rows")
        return df

    except Exception as e:
        raise ValueError(f"Data error: {str(e)}")


# ---------------- Processing ----------------
def process(df, window, logger):
    logger.info("Starting rolling mean computation")

    df["rolling_mean"] = df["close"].rolling(window=window).mean()

    logger.info("Generating signals")
    df["signal"] = (df["close"] > df["rolling_mean"]).astype(int)

    return df


# ---------------- Metrics ----------------
def compute_metrics(df, config, start_time):
    rows_processed = len(df)

    signal_rate = float(df["signal"].mean())

    latency_ms = int((time.time() - start_time) * 1000)

    return {
        "version": config["version"],
        "rows_processed": rows_processed,
        "metric": "signal_rate",
        "value": round(signal_rate, 4),
        "latency_ms": latency_ms,
        "seed": config["seed"],
        "status": "success"
    }


# ---------------- Main ----------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log-file", required=True)
    args = parser.parse_args()

    logger = setup_logger(args.log_file)

    start_time = time.time()

    try:
        logger.info("Job started")

        config = load_config(args.config, logger)

        # seed for reproducibility
        np.random.seed(config["seed"])

        df = load_data(args.input, logger)

        df = process(df, config["window"], logger)

        metrics = compute_metrics(df, config, start_time)

        # write metrics
        with open(args.output, "w") as f:
            json.dump(metrics, f, indent=2)

        logger.info("Job completed successfully")

        print(json.dumps(metrics))

    except Exception as e:
        logger.error(str(e))

        error_output = {
            "version": "v1",
            "status": "error",
            "error_message": str(e)
        }

        with open(args.output, "w") as f:
            json.dump(error_output, f, indent=2)

        print(json.dumps(error_output))
        sys.exit(1)


if __name__ == "__main__":
    main()