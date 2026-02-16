# Backup Service

A robust Python-based backup service aimed at automating PostgreSQL database backups, encrypting them using secure standards (`sops` + `age`), and offloading them to S3-compatible object storage.

## Features

*   **PostgreSQL Backup**: Automated dumps of PostgreSQL databases using `pg_dump` (custom format).
*   **Secure Encryption**: Encrypts backups on the fly using [sops](https://github.com/getsops/sops) and [age](https://github.com/FiloSottile/age) before uploading.
*   **S3 Storage**: Uploads encrypted artifacts to any S3-compatible storage (AWS S3, MinIO, etc.).
*   **Restore Capability**: Built-in functionality to restore databases from local backup files.
*   **Docker Ready**: Fully containerized environment with all necessary system tools pre-installed.

## Prerequisites

If running locally (without Docker), you need the following system tools installed:
*   Python 3.x
*   PostgreSQL Client Tools 18 (`pg_dump`, `pg_restore`)
*   `sops`
*   `age`

## Installation

### Using Docker (Recommended)

1.  Build the image:
    ```bash
    docker build -t backup-service .
    ```

### Running Locally

1.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The service is configured via environment variables. You can set these in a `.env` file in the project root.

### PostgreSQL Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `PGHOST` | Database host address | `localhost` |
| `PGPORT` | Database port | `5432` |
| `PGUSER` | Database username | `root` |
| `PGPASSWORD` | **Required**. Database password | - |
| `BACKUPDIR` | Temporary directory for storing dumps | `/tmp` |

### S3 Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `S3_ENDPOINT` | S3 API endpoint URL | `https://nbg1.your-objectstorage.com` |
| `S3_BUCKET_NAME` | **Required**. Storage bucket name | - |
| `S3_REGION_NAME` | S3 region | `nbg1` |
| `S3_ACCESS_KEY_ID` | **Required**. Access key | - |
| `S3_SECRET_KEY` | **Required**. Secret key | - |

### Encryption Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `AGE_PUBLIC_KEY` | **Required**. Public key for `age` encryption | - |
| `SOPS_AGE_KEY_FILE` | **Required**. Path to the `age` key file for decryption (e.g. for restore) | - |

## Usage

The service is controlled via `main.py` CLI arguments.

### Backing up a Database

To backup a specific database and upload it to S3:

```bash
python3 main.py --postgres --backup --db-name my_database --stage prod
```
*   `--postgres`: Activates PostgreSQL mode.
*   `--backup`: Activates backup mode.
*   `--db-name`: The name of the database to backup.
*   `--stage`: (Optional) Adds a prefix to the backup file (e.g., `prod_...`).

### Restoring a Database

To restore a database from a remote S3 backup file:

```bash
python3 main.py --postgres --restore --db-name my_database --backup-file backups/postgres/prod/my_database/enc.my_database_20231027100000.dump
```
*   `--restore`: Activates restore mode.
*   `--backup-file`: Remote S3 path to the encrypted dump file to restore.
*   `--db-name`: The name of the database to restore into.

### Docker Usage Example

```bash
docker run --env-file .env backup-service --postgres --backup --db-name my_database
```