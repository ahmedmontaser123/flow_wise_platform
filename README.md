# Flow Wise

Quick setup guide for running Flow Wise locally.

## Prerequisites

* Git
* Python **3.12**
* Docker
* Conda is optional

---

## 1. Create Python Environment

### Method 1: Windows

**With Conda**

```powershell
conda create -n flow-wise python=3.12 -y
conda activate flow-wise
```

**Without Conda**

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

### Method 2: WSL 2

**With Conda**

```bash
conda create -n flow-wise python=3.12 -y
conda activate flow-wise
```

**Without Conda**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### Method 3: Linux

**With Conda**

```bash
conda create -n flow-wise python=3.12 -y
conda activate flow-wise
```

**Without Conda**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

---

## 2. Configure `.env`

Copy the example environment file:

### Windows

```powershell
Copy-Item src/.env.example src/.env
```

### WSL / Linux

```bash
cp src/.env.example src/.env
```

Open `src/.env` and fill in the required values:

```env
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

PGADMIN_DEFAULT_EMAIL=
PGADMIN_DEFAULT_PASSWORD=
```

> Keep `src/.env` private. Do not commit it to Git.

---

## 3. Start Docker Services

Go to the **repository root** first:

```bash
cd /path/to/flow-wise
```

Then run:

```bash
docker compose --env-file src/.env -f Docker/docker-compose.yml up -d
```

Check the services:

```bash
docker compose --env-file src/.env -f Docker/docker-compose.yml ps
```

---

## 4. Install Python Dependencies

Make sure your Python environment is activated:

```bash
python -m pip install --upgrade pip
python -m pip install -r src/requirements.txt
```

---

## 5. Stop Docker Services

From the repository root:

```bash
docker compose --env-file src/.env -f Docker/docker-compose.yml down
```

### Default Services

* PostgreSQL: `localhost:5432`
* pgAdmin: `http://localhost:5050`
