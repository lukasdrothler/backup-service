from dotenv import load_dotenv
from src.postgres_backup import *

import logging
import argparse

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S'
)

def main():
    parser = argparse.ArgumentParser(description='Backup service')
    # general arguments
    parser.add_argument('--unencrypted', action='store_true', help='Encrypt files before upload')
    parser.add_argument('--stage', type=str, help='Stage of the environment')
    # specific postgres arguments
    parser.add_argument('--postgres', action='store_true', help='Backup PostgreSQL database')
    parser.add_argument('--db-name', type=str, help='Database name')
    parser.add_argument('--restore', action='store_true', help='Restore PostgreSQL database from backup')
    parser.add_argument('--backup-file', type=str, help='Backup file to restore from')

    args = parser.parse_args()

    # use stages for naming convention, so inte would not overwrite prod
    if args.stage:
        stage = args.stage
    else:
        stage = ""

    if args.postgres:
        if not args.restore:
            backup_postgres(stage, args.db_name)
        else:
            if args.backup_file:
                restore_postgres(args.backup_file, args.db_name)
            else:
                raise ValueError("Backup file must be specified for restore")
    else:
        print("Use arguments to choose an action")



if __name__ == "__main__":
    main()