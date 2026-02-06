from src.manager.s3_manager import S3Manager
from src.manager.postgres_manager import PostgresManager

import logging, os

logger = logging.getLogger(__name__)

def backup_postgres():
    logger.info("Starting PostgreSQL backup")
    pg_manager = PostgresManager()
    s3_manager = S3Manager()

    pgdump_file = pg_manager.pg_dump()
    remote_file_basename = os.path.basename(pgdump_file)

    s3_manager.upload_file(pgdump_file, f"pgdumps/enc.{remote_file_basename}", encrypt=True)
    logger.info("PostgreSQL backup completed")

def restore_postgres(backup_file):
    logger.info("Starting PostgreSQL restore")
    pg_manager = PostgresManager()
    pg_manager.restore_backup(backup_file)
    logger.info("PostgreSQL restore completed")

