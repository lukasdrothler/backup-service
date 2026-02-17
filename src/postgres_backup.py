from src.manager.s3_manager import S3Manager
from src.manager.postgres_manager import PostgresManager

import logging, os

logger = logging.getLogger(__name__)


def backup_postgres(stage=None, db_name=None):
    logger.info("Starting PostgreSQL backup")
    pg_manager = PostgresManager(db_name, stage)
    s3_manager = S3Manager()

    pgdump_file = pg_manager.pg_dump()
    remote_file_basename = os.path.basename(pgdump_file)
    stage_dir = ""
    if stage is not None and stage != "" and stage.lower() != "prod":
        stage_dir = f"{stage}/"
    if db_name is not None and db_name != "":
        db_name_dir = f"{db_name}/"
    s3_filename = f"backups/postgres/{stage_dir}{db_name_dir}enc.{remote_file_basename}"
    s3_manager.upload_file(pgdump_file, s3_filename, encrypt=True)

    logger.info("PostgreSQL backup completed")


def restore_postgres(remote_backup_file, db_name, delete_local_backup=True):
    logger.info("Starting PostgreSQL restore")
    pg_manager = PostgresManager(db_name)
    s3_manager = S3Manager()

    local_backup_file = os.path.join("/tmp", os.path.basename(remote_backup_file)) # nosec
    
    logger.info (f"Downloading backup file from S3: {remote_backup_file} to {local_backup_file}")
    decryped_backup_file = s3_manager.download_file(remote_backup_file, local_backup_file, decrypt=True)

    try:
        logger.info(f"Restoring PostgreSQL database '{db_name}' from backup file '{decryped_backup_file}'")
        pg_manager.restore_backup(decryped_backup_file)
    except Exception as e:
        logger.error(f"Failed to restore PostgreSQL database '{db_name}' from backup file '{decryped_backup_file}'. Error: {e}")
        raise e
    finally:
        if delete_local_backup:
            os.remove(decryped_backup_file)
            logger.info(f"Deleted local backup file: {decryped_backup_file}")
    logger.info("PostgreSQL restore completed")

