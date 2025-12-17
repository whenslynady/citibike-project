# -----------------------------
# Base image (Astro Runtime)
# -----------------------------
FROM astrocrpublic.azurecr.io/runtime:3.1-3

# -----------------------------
# Switch to root to install system packages
# -----------------------------
USER root

RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
        vim \
        curl \
        unzip \
        lsb-release \
        apt-transport-https \
        git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Create directories for credentials and DBT configs
# -----------------------------
RUN mkdir -p /opt/airflow/.google/credentials \
    && mkdir -p /opt/airflow/.dbt \
    && mkdir -p /opt/airflow/dbt

#&& mkdir -p /opt/airflow/dags \
#&& mkdir -p /opt/airflow/tests

# -----------------------------
# Copy GCP credentials into the container
# -----------------------------
COPY .google/credentials/google_credentials.json /opt/airflow/.google/credentials/google_credentials.json

RUN chown astro:astro /opt/airflow/.google/credentials/google_credentials.json \
    && chmod 600 /opt/airflow/.google/credentials/google_credentials.json

# -----------------------------
# Copy REAL DBT project folder
# -----------------------------
# IMPORTANT: This must contain dbt_project.yml, models/, macros/, etc.
COPY .dbt/citibike_dbt_gcp/ /opt/airflow/dbt/

# -----------------------------
# Copy DBT profiles.yml
# -----------------------------
COPY .dbt/profiles.yml /opt/airflow/.dbt/profiles.yml


# -----------------------------
# Copy Dags on container
# -----------------------------
#COPY dags /opt/airflow/dags

# -----------------------------
# Copy tests on container
# -----------------------------
#COPY tests/dags /opt/airflow/tests


# -----------------------------
# Fix DBT permissions
# -----------------------------
RUN chown -R astro:astro /opt/airflow/dbt /opt/airflow/.dbt \
    && chmod -R 755 /opt/airflow/dbt /opt/airflow/.dbt

# -----------------------------
# Switch back to Astro user
# -----------------------------
USER astro

# -----------------------------
# Install Python packages
# -----------------------------
RUN pip install --no-cache-dir \
    dbt-core \
    dbt-bigquery \
    google-cloud-storage \
    pandas \
    pyarrow \
    apache-airflow-providers-google \
    apache-airflow-providers-dbt-cloud \
    astronomer-cosmos \
    astronomer-cosmos[google] \
    pytest

# -----------------------------
# Environment variables
# -----------------------------
ENV GOOGLE_APPLICATION_CREDENTIALS="/opt/airflow/.google/credentials/google_credentials.json"
ENV DBT_PROFILES_DIR="/opt/airflow/.dbt"
ENV DBT_PROJECT_DIR="/opt/airflow/dbt"
ENV DBT_TARGET="dev"
ENV TARGET_ENV="dev"
ENV GCP_PROJECT_ID="sound-harbor-480119-v8"
ENV BIGQUERY_DATASET="de_citibike_tripdata_1"
ENV BUCKET="dtc_data_lake_sound-harbor-480119-v8"
ENV PYTHONPATH="/opt/airflow:${PYTHONPATH}"


# -----------------------------
# Set working directory
# -----------------------------
WORKDIR /opt/airflow

# -----------------------------
# Optional: Copy DAGs (if needed)
# -----------------------------
# COPY dags/ /opt/airflow/dags/

