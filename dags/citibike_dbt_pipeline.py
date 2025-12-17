import os
from datetime import datetime
from airflow import DAG
from airflow.operators.empty import EmptyOperator

# Cosmos imports
from cosmos.airflow.task_group import DbtTaskGroup
from cosmos.config import ProfileConfig, ProjectConfig, RenderConfig
from cosmos.constants import LoadMode
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

# ==========================================================
# ENVIRONMENT VARIABLES (take them from Docker / local ENV)
# ==========================================================
AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow")
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "sound-harbor-480119-v8")
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", "de_citibike_tripdata_1")
GCP_CONN_ID = os.environ.get("GCP_CONN_ID", "google_cloud_default")

# Paths for DBT from ENV (no hardcode)
DBT_PROJECT_PATH = os.environ.get("DBT_PROJECT_DIR", "/opt/airflow/dbt")
DBT_PROFILES_DIR = os.environ.get("DBT_PROFILES_DIR", "/opt/airflow/.dbt")
DBT_PROFILE_NAME = os.environ.get("DBT_PROFILE_NAME", "citibike_dbt_gcp")
DBT_TARGET = os.environ.get("DBT_TARGET", "dev")
DBT_EXECUTABLE = os.environ.get("DBT_EXECUTABLE", "/usr/local/bin/dbt")

# ==========================================================
# COSMOS CONFIG
# ==========================================================
DBT_PROFILE_CONFIG = ProfileConfig(
    profile_name=DBT_PROFILE_NAME,
    target_name=DBT_TARGET,
    profiles_yml_filepath=os.path.join(DBT_PROFILES_DIR, "profiles.yml")
)

DBT_PROJECT_CONFIG = ProjectConfig(
    dbt_project_path=DBT_PROJECT_PATH
)

DBT_RUN_RENDER_CONFIG = RenderConfig(
    load_method=LoadMode.DBT_LS,
    select=["path:models"],      # Run all models respecting dependencies
    dbt_executable_path=DBT_EXECUTABLE
)

# ==========================================================
# DAG DEFINITION
# ==========================================================
default_args = {
    "owner": "andy",
    "depends_on_past": False,
    "retries": 1,
    "start_date": datetime(2025, 1, 1),
}

with DAG(
    dag_id="citibike_dbt_pipeline",
    default_args=default_args,
    description="DBT Cosmos workflow for Citibike (run all models in order)",
    schedule=None,
    catchup=False,
    max_active_runs=1,
    tags=["citibike", "dbt", "cosmos"],
) as dag:

    # Start / End operators
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    # -----------------------------
    # DBT run / transformations via Cosmos TaskGroup
    # -----------------------------
    dbt_run = DbtTaskGroup(
        group_id="dbt_transformations",
        project_config=DBT_PROJECT_CONFIG,
        profile_config=DBT_PROFILE_CONFIG,
        render_config=DBT_RUN_RENDER_CONFIG
    )

    # -----------------------------
    # DAG dependencies
    # -----------------------------
    start >> dbt_run >> end
