# 🚲 CitiBike Trip Data – End-to-End Data Pipeline

## 1. Problem Description

CitiBike generates a very large volume of trip data every day.  
Due to the raw, compressed, and unstructured nature of this data, it is not immediately suitable for analysis or reporting.  
Without proper organization and processing, extracting reliable insights from the data becomes challenging.

---

## 📅 Data Analysis Period
**December 30, 2024 – January 31, 2025**

## 📂 Data Source
The raw data used in this project comes from **Citi Bike’s public trip data repository**.

- The data is **publicly available**
- It is provided as **compressed ZIP files**
- Each file contains detailed records of Citi Bike trips for a given month

### 🔗 Official Source
The dataset for this analysis was downloaded directly from the official Citi Bike S3 bucket:

- **Source URL:** https://s3.amazonaws.com/tripdata/202501-citibike-tripdata.zip


### 📄 Dataset Fields

The dataset includes the following attributes:

- Ride ID  
- Rideable type  
- Started at  
- Ended at  
- Start station name  
- Start station ID  
- End station name  
- End station ID  
- Start latitude  
- Start longitude  
- End latitude  
- End longitude  
- Member or casual rider type

---

## 2. Business Questions

1. What is the total number of CitiBike trips during the analysis period?
2. Which start stations generate the highest number of trips?
3. How does ride efficiency differ between electric bikes and classic bikes?
4. What is the distribution of trips by ride duration category (short, medium, long)?
5. How does daily trip volume evolve over time?
6. How do trips compare between members and casual users?

---

## 3. Project Objectives

The objectives of this project are to:

- Prepare and store raw CitiBike trip data in Google Cloud Storage (GCS)
- Organize the raw data into a structured data lake layout
- Load the data into BigQuery as partitioned and clustered tables
- Optimize data for analytical queries and performance
- Build dashboards to visualize key metrics and insights

---



## 4. 🛠️ Technology Overview

1. **Terraform** provisions infrastructure on GCP (VM, storage buckets, datasets).  
2. **Airflow** runs ETL: downloads CitiBike ZIP files, unzips, converts CSV to Parquet, uploads to **GCS**.  
3. **BigQuery** reads data from **GCS**, creating external tables, then partitioned & clustered tables.  
4. **dbt** applies transformations and builds analytical views for reporting.  
5. **Looker Studio** visualizes insights using the transformed data.  


---

## 6. High-Level Architecture

```
![Data Pipeline Architecture](images/data_pipeline.png)

```

---

## 7. Project Structure

```
citibike-data-pipeline/
│
├── Dockerfile
├── README.md
├── airflow_settings.yaml
├── dags 
│   ├── citibike_dbt_pipeline.py
│   ├── citibike_to_gcs_2025.py
│   └── gcs_to_bigquery_2025.py
├── dbt_env
├── .dbt
│   ├── citibike_dbt_gcp
│   └── profiles.yml
│   
├── images
├── include
├── logs
├── packages.txt
├── plugins
├── requirements.txt
├── terraform
│   ├── main.tf
│   └── variables.tf
└── tests
    └── dags

---

## 7. 📊 Data Visualizations

Data visualizations for this project can be accessed [here](https://lookerstudio.google.com/reporting/8b4b0a39-9df0-4788-83d2-1aa8bd57524f).  

![Insert Dashboard Screenshot Here](path/to/your/image.png)




## 8. 🔄 Reproduce Project

To reproduce the project and test the code yourself, follow these steps.  
For a **complete step-by-step guide**, you can access it [here](link-to-full-guide.md).









````markdown
# ✅ STEP 1 — Full GCP Project Setup  
**GCP Project + VM + Service Account + SSH + JSON Configuration**

This step prepares the complete Google Cloud environment required to run the CitiBike data pipeline.

---

## 1️⃣ Create the GCP Project

![Insert Dashboard Screenshot Here](/image.foto2.png)

1. Open **Google Cloud Console**  
2. Select your organization/location if required  
3. Click **Create Project**  
4. Set project name: `de-citibike-data-pipeline`  
5. Click **Create**  
6. Select the newly created project  
7. Copy and save:
   - Project Name  
   - Project Number  
   - Project ID  

---

## 2️⃣ Enable Compute Engine API

![Insert Dashboard Screenshot Here](/image.foto5.png)

1. In the search bar, type **Compute Engine**  
2. Open it and wait until the API is enabled  

---

## 3️⃣ Create the VM Instance

![Insert Dashboard Screenshot Here](/image.foto6.png)

1. Search for **VM Instances**  
2. Click **Create Instance**  

### General
- Name: `instance-citibike-data`  
- Region: `us-central1 (Iowa)`  
- Zone: `us-central1-c`  

### Machine Configuration
- Machine type: `e2-standard-4`  
  - 4 vCPUs  
  - 16 GB RAM  

### Boot Disk
- OS: Ubuntu  
- Version: Ubuntu 22.04 LTS  
- Disk type: Balanced Persistent Disk  
- Size: 40 GB  

3. Click **Create**

---

## 4️⃣ Create the Service Account

![Insert Dashboard Screenshot Here](/image.foto...png)

1. Go to **IAM & Admin → Service Accounts**  
2. Click **Create Service Account**  
3. Name: `serv-acct`  
4. Click **Create and Continue**  

### Assign Roles
- Basic → Viewer  
- Storage → Storage Object Admin  
- Storage → Storage Admin  
- BigQuery → BigQuery Admin  

5. Click **Done**

---

## 5️⃣ Create the JSON Key

![Insert Dashboard Screenshot Here](/image.foto......png)

1. Open the service account (`serv-acct`)  
2. Click **Manage Keys**  
3. Click **Add Key → Create new key**  
4. Select **JSON**  
5. Download the key file  

⚠️ Keep this file safe. It will be uploaded to the VM.

---

## 6️⃣ Prepare SSH Keys (Ubuntu / WSL)

![Insert Dashboard Screenshot Here](/image.foto19.png)

```bash
cd ~/.ssh
mkdir -p ~/.ssh
chmod 700 ~/.ssh

ssh-keygen -t rsa -f ~/.ssh/gcp -C whensly -b 2048
````

Press **Enter** through all prompts.

Show the public key:

```bash
cat ~/.ssh/gcp.pub
```

---

## 7️⃣ Add SSH Key to GCP Metadata

![Insert Dashboard Screenshot Here](/image.foto20.png)

1. Copy the full output of `gcp.pub`
2. Go to **Compute Engine → Metadata**
3. Open **SSH Keys**
4. Click **Edit → Add SSH Key**
5. Paste the public key
6. Click **Save**

---

## 8️⃣ Create SSH Config File

![Insert Dashboard Screenshot Here](/image.foto22.png)

```bash
nano ~/.ssh/config
```

To simplify connecting to your VM, we create an SSH configuration file.  
This allows you to use a simple alias (`instance-citibike-data`) instead of typing the full IP, username, and key path each time.

Paste:

```text
Host instance-citibike-data
    Hostname 34.69.252.0      # External IP of your VM
    User whensly               # Username on the VM
    IdentityFile /home/whensly/.ssh/gcp  # Path to your private SSH key
```

Save:

* **Ctrl + O** → Enter
* **Ctrl + X**

---

## 9️⃣ Connect to the VM

![Insert Dashboard Screenshot Here](/image.foto23.png)

```bash
ssh instance-citibike-data
```

Type `yes` to confirm the fingerprint.

---

## 🔟 Upload JSON Key Using SFTP

![Insert Dashboard Screenshot Here](/image.foto24.png)

```bash
sftp instance-citibike-data
```

```bash
lcd /mnt/c/Users/whens/Downloads
put your-service-account-key.json
exit
```

---

## 1️⃣1️⃣ Move JSON Key Inside the VM

```bash
ssh instance-citibike-data
mkdir -p ~/.google/credentials
cp ~/your-service-account-key.json ~/.google/credentials/google_credentials.json
ls -l ~/.google/credentials/
```

---

## 1️⃣2️⃣ Set Environment Variable


```bash
echo 'export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.google/credentials/google_credentials.json"' >> ~/.bashrc
source ~/.bashrc
echo $GOOGLE_APPLICATION_CREDENTIALS
```

---

## 1️⃣3️⃣ Activate Service Account with gcloud


```bash
gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS
```

---






````markdown
# ✅ STEP 2 — INSTALL ALL ENGINEERING TOOLS ON THE VM

This step installs all the necessary engineering tools on your VM to run the CitiBike data pipeline.

---

## 1️⃣ Install Anaconda (Linux Version)

Go to the repository:  
https://repo.anaconda.com/archive/

1. Choose the Ubuntu Linux installer:  
   Select `Anaconda3-2025.xx-Linux-x86_64.sh` (pick the latest from 2025)
2. Open your VM terminal
3. Download the installer:
```bash
wget https://repo.anaconda.com/archive/Anaconda3-2025.06-1-Linux-x86_64.sh
````

4. Verify the file is downloaded:

```bash
ls
# You should see: Anaconda3-2025.06-1-Linux-x86_64.sh
```

5. Run the installer:

```bash
bash Anaconda3-2025.06-1-Linux-x86_64.sh
```

6. During installation:

   * Press Enter to scroll
   * Type **yes** when asked to accept
   * Type **yes** again when asked to initialize Conda

Anaconda will be installed and activated automatically.

---

### 1.3 Initialize Conda

```bash
~/anaconda3/bin/conda init
source ~/.bashrc
conda activate base
```

### 1.4 Optional: Add Conda to PATH Manually

```bash
ls /home/whensly/anaconda3
export PATH="/home/whensly/anaconda3/bin:$PATH"
```

### 1.5 Verify Installation

```bash
conda --version
which conda
```

---

## 2️⃣ Install Terraform

### 2.1 Add HashiCorp GPG Key

```bash
wget -O - https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
```

### 2.2 Add Terraform Repo

```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(grep -oP '(?<=UBUNTU_CODENAME=).*' /etc/os-release || lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
```

### 2.3 Install Terraform

```bash
sudo apt update && sudo apt install terraform
```

### 2.4 Verify Installation

```bash
terraform -version
which terraform
```

---

## 3️⃣ Install Docker Compose (Latest Release from GitHub)

### 3.1 Create Tools Directory

```bash
mkdir -p ~/bin
cd ~/bin
```

### 3.2 Download Docker Compose

```bash
wget https://github.com/docker/compose/releases/download/v5.0.0/docker-compose-linux-x86_64 -O docker-compose
chmod +x docker-compose
```

### 3.3 Add to PATH

```bash
export PATH="$HOME/bin:$PATH"
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 3.4 Verify

```bash
docker-compose -v
```

---

## 4️⃣ Install Docker Engine

### 4.1 Install Docker

```bash
sudo apt-get update
sudo apt-get install docker.io
```

### 4.2 Verify Docker

```bash
docker -v
which docker
```

### 4.3 Allow Docker Without sudo

```bash
sudo groupadd docker
sudo gpasswd -a $USER docker
sudo service docker restart
```

### 4.4 Test Docker

```bash
docker run hello-world
```

If permission fails → logout and reconnect:

```bash
exit
ssh instance-citibike-data
docker run hello-world
```

---

## 5️⃣ Install Astronomer (Astro CLI)

```bash
curl -sSL https://install.astronomer.io | sudo bash
astro --version
which astro
```

---

## 6️⃣ Install dbt-bigquery (Using a Clean Virtual Environment)

### 6.1 Deactivate Conda

```bash
conda deactivate
```

### 6.2 Create Virtualenv

```bash
python3 -m venv dbt_env
```

### 6.3 Activate It

```bash
source dbt_env/bin/activate
# Prompt should show: (dbt_env)
```

### 6.4 Install dbt-bigquery

```bash
pip install --upgrade pip
pip install dbt-bigquery
```

### 6.5 Initialize dbt Project

```bash
dbt init citibike_dbt_gcp
```

### 6.6 Verify dbt Installation

```bash
dbt --version
which dbt
```

```





````markdown
# ✅ STEP 3 — Complete Ubuntu Environment Setup  
**Configure Anaconda, Custom PATH, and Google Cloud Credentials**

This step ensures that Anaconda, custom PATH, and GCP credentials are correctly set for all terminal sessions.

---

## 1️⃣ Open the `.bashrc` File
In your Ubuntu VM terminal:
```bash
nano ~/.bashrc
````

---

## 2️⃣ Add Final Configuration

Paste this block at the bottom of the file:

```bash
# ---------------------------------------------------------
# Add custom ~/bin directory to PATH
export PATH="$HOME/bin:$PATH"

# ---------------------------------------------------------
# Activate base Anaconda automatically
source ~/anaconda3/bin/activate

# ---------------------------------------------------------
# Set Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.google/credentials/google_credentials.json"
```

**Notes:**

* Ensure the paths match your username (`whensly`)
* Make sure the credentials file exists in `~/.google/credentials/`

---

## 3️⃣ Save and Close `.bashrc`

Inside nano:

* **Ctrl + O** → Enter (save)
* **Ctrl + X** (exit)

---

## 4️⃣ Reload `.bashrc` or Restart Terminal

```bash
source ~/.bashrc
```

Test activation:

```bash
conda activate
conda deactivate
```

---

## 5️⃣ Verify Configuration

### 5.1 Verify Anaconda Base Environment

```bash
conda info --envs
```

Expected output:

```
# conda environments:
base  *  /home/whensly/anaconda3
```

The `(base)` prefix should appear in your terminal.

### 5.2 Verify PATH

```bash
echo $PATH
```

Expected to include:

```
/home/whensly/bin:/home/whensly/anaconda3/bin:...
```

### 5.3 Verify Google Cloud Credentials

```bash
echo $GOOGLE_APPLICATION_CREDENTIALS
```

Expected:

```
/home/whensly/.google/credentials/google_credentials.json
```

```
```




````markdown
# ✅ STEP 4 — Remote-SSH Setup in VS Code (Windows → Linux)

This step configures Remote-SSH in VS Code to connect from Windows to your Ubuntu VM.

---

## 1️⃣ Open Command Prompt
Press **Windows + R**, type:
```text
cmd
````

and hit **Enter**.

---

## 2️⃣ Create Your `.ssh` Folder on Windows

```cmd
mkdir C:\Users\whens\.ssh
```

Check the directory:

```cmd
dir C:\Users\whens\
```

Go into the folder:

```cmd
cd C:\Users\whens\.ssh
```

You should see these files:

* `config`
* `gcp`
* `gcp.pub`
* `known_hosts`

---

## 3️⃣ If Files Are Missing

Open Ubuntu terminal and copy the SSH files from Linux to Windows:

Check files in Linux:

```bash
cd ~/.ssh
ls
```

Expected files:

* `config`
* `gcp`
* `gcp.pub`
* `known_hosts`

Copy them to Windows:

```bash
cp ~/.ssh/config ~/.ssh/gcp ~/.ssh/gcp.pub ~/.ssh/known_hosts /mnt/c/Users/whens/.ssh/
```

---

## 4️⃣ Edit Your SSH Config on Windows

Open the config file:

```cmd
notepad config
```

or

```cmd
notepad C:\Users\whens\.ssh\config
```

Add or update this block:

```text
Host instance-citibike-data
    HostName 34.60.252.0
    User whensly
    IdentityFile C:\Users\whens\.ssh\gcp
```

---

## 5️⃣ Important Path Notes

* **Ubuntu path:**
  `IdentityFile /home/whensly/.ssh/gcp`
* **Windows path for VS Code:**
  `IdentityFile C:\Users\whens\.ssh\gcp`

---

## 6️⃣ Meaning of Each Field

* **Host** → Shortcut name for your connection (VM instance)
* **HostName** → External IP address of your VM
* **User** → Linux username on the VM
* **IdentityFile** → Path to your private SSH key

---

## 7️⃣ Save the Config

Press **Ctrl + S**, then close Notepad.
You are now ready to use VS Code Remote-SSH to connect to your Ubuntu VM.

```
```



````markdown
# ✅ STEP 5 — Connect to Your VM Using Remote-SSH in VS Code

This step explains how to connect to your Ubuntu VM from Windows using VS Code Remote-SSH.

---

## 1️⃣ Open VS Code
You can open it from the icon or from Command Prompt:

```cmd
code .
````

This opens VS Code in the current folder (e.g., `C:\Users\whens\.ssh`).
Make sure the `code` command works. If it doesn’t, enable **“Add to PATH”** during VS Code installation.

---

## 2️⃣ Install the Remote-SSH Extension

In VS Code:

1. Click the **Extensions** icon (left sidebar)
2. Search for: `Remote - SSH`
3. Click **Install**

---

## 3️⃣ Connect to Your VM

1. Press **Ctrl + Shift + P**
2. Search for: `Remote-SSH: Connect to Host…`
3. Select: `instance-citibike-data`

VS Code will ask:

* **Remote platform:** choose Linux
* **Host authenticity / fingerprint:** click **Continue**

VS Code will automatically:

* Install the VS Code server on the VM (`~/.vscode-server`)
* Start your SSH session
* Open a new VS Code window connected to your VM

---

## 🔑 Important Notes

1. **SSH private key permissions (on the VM):**

```bash
chmod 600 ~/.ssh/gcp
```

2. **Verify identity file path on Windows:**
   `IdentityFile C:\Users\whens\.ssh\gcp`

3. **Do NOT add `.pem`**
   Your key is already in OpenSSH format. Never rename it to `.pem`.

---

## 4️⃣ Activate Your GCP Service Account

In the VS Code terminal (inside your VM):

```bash
gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS
```

This ensures your GCP permissions are active and ready.

---

## 5️⃣ Optional: Initialize Astro Airflow Project

```bash
mkdir citibike_pipeline
cd citibike_pipeline
astro dev init
```

This initializes your Astro Airflow environment inside the VM.

```
```










