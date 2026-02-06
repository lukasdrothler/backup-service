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
    parser.add_argument('--unencrypted', action='store_true', help='Encrypt files before upload')
    parser.add_argument('--postgres', action='store_true', help='Backup PostgreSQL database')
    parser.add_argument('--restore', action='store_true', help='Restore PostgreSQL database from backup')
    parser.add_argument('--backup-file', type=str, help='Backup file to restore from')
    args = parser.parse_args()
    if args.postgres:
        if not args.restore:
            backup_postgres()
        else:
            if args.backup_file:
                restore_postgres(args.backup_file)
            else:
                raise ValueError("Backup file must be specified for restore")



if __name__ == "__main__":
    main()
