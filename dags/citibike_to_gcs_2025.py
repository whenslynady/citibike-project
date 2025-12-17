import os
import logging
from datetime import datetime
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.models import Variable
from airflow.operators.trigger_dagrun import TriggerDagRunOperator


# ==========================================================
# 🔧 GENERAL CONFIGURATION
# ==========================================================
AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow")
DATA_FOLDER = os.path.join(AIRFLOW_HOME, "data")
os.makedirs(DATA_FOLDER, exist_ok=True)

# --- GCP CONFIG ---
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "sound-harbor-480119-v8")
BUCKET = os.environ.get("GCP_GCS_BUCKET", "dtc_data_lake_sound-harbor-480119-v8")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", "de_citibike_tripdata_1")
GCP_CONN_ID = Variable.get("GCP_CONN_ID", default_var="google_cloud_default")

# --- GCP CREDENTIALS ---
GOOGLE_APPLICATION_CREDENTIALS = "/opt/airflow/.google/credentials/google_credentials.json"
if not os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
    raise FileNotFoundError(
        f"❌ Credential file not found at {GOOGLE_APPLICATION_CREDENTIALS}"
    )
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

# --- DATASET INFO ---
dataset_zip = "202501-citibike-tripdata.zip"
dataset_url = f"https://s3.amazonaws.com/tripdata/{dataset_zip}"

# ==========================================================
# 🧩 FUNCTIONS
# ==========================================================
def format_to_parquet(**context):
    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]
    if not files:
        logging.error("❌ No CSV files found in the data folder.")
        return

    for csv_file in files:
        src_file = os.path.join(DATA_FOLDER, csv_file)

        try:
            df = pd.read_csv(src_file)

            # --- Fix datetime fields ---
            for col in ["started_at", "ended_at"]:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce")

            # --- Fix station ids ---
            for col in ["start_station_id", "end_station_id"]:
                if col in df.columns:
                    df[col] = df[col].astype("string")

            # --- Soft normalize column names (BigQuery strict) ---
            df.columns = (
                df.columns
                .str.strip()
                .str.lower()
                .str.replace(" ", "_")
                .str.replace("-", "_")
            )

            # --- Add partition column (MUST BE DATE TYPE) ---
            if "started_at" in df.columns:
                df["started_at_date"] = pd.to_datetime(df["started_at"]).dt.date
                df["started_at_date"] = pd.to_datetime(df["started_at_date"]).dt.date

            # --- Ensure deterministic schema (sort columns) ---
            df = df.reindex(sorted(df.columns), axis=1)

            # --- Convert to Parquet with Arrow schema ---
            table = pa.Table.from_pandas(df, preserve_index=False)

            pq_file = src_file.replace(".csv", ".parquet")
            pq.write_table(table, pq_file)

            logging.info(f"✅ BigQuery-ready Parquet created: {pq_file}")

        except Exception as e:
            logging.error(f"⚠️ Error converting {csv_file}: {e}")



def upload_to_gcs(**context):
    """Upload all Parquet files in the data folder to GCS using the Airflow connection."""
    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".parquet")]
    if not files:
        logging.error("❌ No Parquet files found to upload.")
        return

    # Optimize upload chunks
    from google.cloud import storage
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024

    gcs_hook = GCSHook(gcp_conn_id=GCP_CONN_ID)
    bucket_obj = gcs_hook.get_bucket(BUCKET)

    for pq_file in files:
        local_file = os.path.join(DATA_FOLDER, pq_file)
        object_name = f"raw/{pq_file}"

        try:
            blob = bucket_obj.blob(object_name)
            blob.upload_from_filename(local_file)
            logging.info(
                f"✅ Uploaded {pq_file} → gs://{BUCKET}/{object_name}"
            )
        except Exception as e:
            logging.error(f"⚠️ Upload failed for {pq_file}: {e}")

# ==========================================================
# 🌀 DAG DEFINITION
# ==========================================================
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "start_date": datetime(2025, 1, 1),
}

with DAG(
    dag_id="citibike_to_gcs_2025",
    default_args=default_args,
    description="Extract Citibike data, convert to Parquet, and upload to GCS",
    schedule="@daily",
    catchup=True,
    max_active_runs=1,
    tags=["citibike", "gcs", "etl"],
) as dag:

    # 1️⃣ Download ZIP dataset
    download_dataset_task = BashOperator(
        task_id="download_dataset",
        bash_command=f"curl -sSL {dataset_url} -o {DATA_FOLDER}/{dataset_zip}",
    )

    # 2️⃣ Unzip dataset
    unzip_data_task = BashOperator(
        task_id="unzip_data",
        bash_command=f"unzip -o {DATA_FOLDER}/{dataset_zip} -d {DATA_FOLDER}",
    )

    # 3️⃣ Convert CSV → Parquet
    format_to_parquet_task = PythonOperator(
        task_id="convert_to_parquet",
        python_callable=format_to_parquet,
    )

    # 4️⃣ Upload to GCS
    upload_to_gcs_task = PythonOperator(
        task_id="upload_to_gcs",
        python_callable=upload_to_gcs,
    )


    # 5️⃣ Trigger DAG 2
    trigger_gcs_to_bq = TriggerDagRunOperator(
        task_id="trigger_gcs_to_bigquery",
        trigger_dag_id="gcs_to_bigquery_2025",
        wait_for_completion=False
    )
    # DAG dependencies
    download_dataset_task >> unzip_data_task >> format_to_parquet_task >> upload_to_gcs_task >> trigger_gcs_to_bq

    
