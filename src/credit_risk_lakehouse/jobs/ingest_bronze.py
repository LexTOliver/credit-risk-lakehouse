from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

import kagglehub  # type: ignore[import-untyped]
from pyspark.sql import SparkSession

from credit_risk_lakehouse.utils.logging import get_logger, setup_logging

LOGGER = get_logger(__name__)

SOURCES = {
    "application_train": "application_train.csv",
    "bureau": "bureau.csv",
    "previous_application": "previous_application.csv",
}

LANDING_SCHEMA = "landing"
BRONZE_SCHEMA = "bronze"
VOLUME_NAME = "home_credit_default_risk"


def parse_args() -> argparse.Namespace:
    """Set up command line arguments."""
    parser = argparse.ArgumentParser(
        description="Ingest bronze data from Home Credit into the lakehouse"
    )

    parser.add_argument(
        "--catalog",
        type=str,
        default="credit_risk_lakehouse",
        help="The name of the catalog to use for the lakehouse",
    )

    parser.add_argument(
        "--mode",
        choices=("bootstrap", "rebuild"),
        default="bootstrap",
        help=(
            "The mode to use for ingestion. "
            "'bootstrap' provisions the lakehouse, downloads the data, rebuilds Bronze;"
            " 'rebuild' validates existing landing files and rebuilds Bronze."
        ),
    )

    return parser.parse_args()


def initialize_lakehouse(spark: SparkSession, catalog: str) -> None:
    """Initialize the lakehouse for ingestion creating catalog, schemas and volume."""
    # Create and set the catalog if it doesn't exist
    spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog}")
    spark.sql(f"USE CATALOG {catalog}")

    # Create the landing and bronze schemas if they don't exist
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {LANDING_SCHEMA}")
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {BRONZE_SCHEMA}")

    # Create the volume if it doesn't exist
    spark.sql(f"CREATE VOLUME IF NOT EXISTS {LANDING_SCHEMA}.{VOLUME_NAME}")


def download_data(catalog: str) -> None:
    """Download the Home Credit data from Kaggle Hub."""
    output_dir = f"/Volumes/{catalog}/{LANDING_SCHEMA}/{VOLUME_NAME}"

    kagglehub.competition_download("home-credit-default-risk", output_dir=output_dir)


def validate_landing_files(catalog: str) -> None:
    """Ensure required landing files exist in the specified catalog."""
    volume_path = Path(f"/Volumes/{catalog}/{LANDING_SCHEMA}/{VOLUME_NAME}")
    missing_files = [
        filename
        for filename in SOURCES.values()
        if not (volume_path / filename).exists()
    ]
    if missing_files:
        raise FileNotFoundError(f"Missing landing files: {', '.join(missing_files)}")


def ingest_source(source: str, filename: str, catalog: str, spark: SparkSession) -> int:
    """Ingest a single source into the lakehouse."""
    source_path = f"/Volumes/{catalog}/{LANDING_SCHEMA}/{VOLUME_NAME}/{filename}"
    target = f"{BRONZE_SCHEMA}.{source}"

    # Ingest the source into the bronze schema
    spark.sql(f"""
        CREATE OR REPLACE TABLE {target}
        USING DELTA AS
        SELECT
            src.*,
            src._metadata.file_path AS _source_path,
            current_timestamp() AS _ingested_at
        FROM read_files(
            '{source_path}',
            format => 'csv',
            header => true,
            infer_schema => false
        ) AS src
    """)

    # Check if the table is empty after ingestion
    total = spark.table(target).count()
    if total == 0:
        raise ValueError(
            f"Empty table {target} after ingestion. "
            f"Check the source file {source_path} for data."
        )

    return total


def ingest_bronze(
    spark: SparkSession,
    catalog: str,
    mode: str,
) -> None:
    """Ingest bronze data from Home Credit into the lakehouse."""
    LOGGER.info("Starting bronze data ingestion...")
    start_time = time.time()

    if mode == "bootstrap":
        # Initialize the lakehouse for ingestion
        LOGGER.info(f"Initializing lakehouse in {catalog}.")
        initialize_lakehouse(spark, catalog)

        # Download the Home Credit data from Kaggle Hub
        LOGGER.info("Downloading Home Credit data from Kaggle Hub.")
        download_data(catalog)
    elif mode == "rebuild":
        LOGGER.info("Rebuilding bronze data from existing catalog and landing files.")
        spark.sql(f"USE CATALOG {catalog}")
    else:
        raise ValueError(f"Invalid mode {mode}. Must be 'bootstrap' or 'rebuild'.")

    # Validate that the required landing files exist
    validate_landing_files(catalog)

    # Ingest each source into the lakehouse
    for source, filename in SOURCES.items():
        LOGGER.info(f"Ingesting source {source} from file {filename}.")
        total_count = ingest_source(source, filename, catalog, spark)
        LOGGER.info(f"Total rows ingested for {source}: {total_count}")

    end_time = time.time()
    LOGGER.info(
        "Bronze data ingestion completed successfully "
        f"in {end_time - start_time:.2f} seconds."
    )


def main() -> None:
    """Main entry point for the script."""
    args = parse_args()
    setup_logging(level_name=os.getenv("LOG_LEVEL", "INFO"))

    # Create a Spark session
    spark = SparkSession.builder.appName("Ingest Bronze Data").getOrCreate()
    LOGGER.debug("Spark session created.")

    # Ingest the bronze data
    ingest_bronze(spark, args.catalog, args.mode)


if __name__ == "__main__":
    main()
