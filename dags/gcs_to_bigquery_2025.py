import os
from datetime import datetime
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.models import Variable
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

# -----------------------------
# 🔧 Variables / Environment
# -----------------------------
# --- GCP CONFIG ---
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "sound-harbor-480119-v8")
BUCKET = os.environ.get("GCP_GCS_BUCKET", "dtc_data_lake_sound-harbor-480119-v8")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", "de_citibike_tripdata_1")
GCP_CONN_ID = Variable.get("GCP_CONN_ID", default_var="google_cloud_default")

EXTERNAL_TABLE = "external_citibike_tripdata_2025"
INTERNAL_TABLE = "citibike_tripdata_partitioned_2025"


# -----------------------------
# 🧩 Default Args
# -----------------------------
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "start_date": datetime(2025, 1, 1),
}

# -----------------------------
# 🗂️ DAG Definition
# -----------------------------
with DAG(
    dag_id="gcs_to_bigquery_2025",
    default_args=default_args,
    description="Load Citibike parquet files from GCS to BigQuery (External + Partitioned Table)",
    schedule=None,  # triggered manually or by previous DAG
    catchup=False,
    max_active_runs=1,
    tags=["citibike", "gcs", "bigquery"],
) as dag:

    # 1️⃣ Create External Table (read directly from GCS)
    CREATE_EXTERNAL_TABLE_QUERY = f"""
    CREATE OR REPLACE EXTERNAL TABLE `{PROJECT_ID}.{BIGQUERY_DATASET}.{EXTERNAL_TABLE}`
    OPTIONS(
        format = 'PARQUET',
        uris = ['gs://{BUCKET}/raw/*.parquet']
    );
    """

    create_external_table = BigQueryInsertJobOperator(
        task_id="create_external_table",
        configuration={
            "query": {
                "query": CREATE_EXTERNAL_TABLE_QUERY,
                "useLegacySql": False,
            }
        },
        gcp_conn_id=GCP_CONN_ID
    )

    # 2️⃣ Create Partitioned Internal Table (based on started_at_date)
    CREATE_PARTITIONED_TABLE_QUERY = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{BIGQUERY_DATASET}.{INTERNAL_TABLE}`
    PARTITION BY started_at_date
    AS
    SELECT *
    FROM `{PROJECT_ID}.{BIGQUERY_DATASET}.{EXTERNAL_TABLE}`;
    """

    create_partitioned_table = BigQueryInsertJobOperator(
        task_id="create_partitioned_table",
        configuration={
            "query": {
                "query": CREATE_PARTITIONED_TABLE_QUERY,
                "useLegacySql": False,
            }
        },
        gcp_conn_id=GCP_CONN_ID
    )

    # Trigger DAG 3
    trigger_dbt_pipeline = TriggerDagRunOperator(
    task_id="trigger_citibike_dbt_pipeline",
    trigger_dag_id="citibike_dbt_pipeline",
    wait_for_completion=False,   # pa ret tann DAG 3 fini
    )

    # -----------------------------
    # 🔗 Dependencies
    # -----------------------------
    create_external_table >> create_partitioned_table >> trigger_dbt_pipeline

    

