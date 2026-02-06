import logging, os, subprocess
from datetime import datetime

logger = logging.getLogger(__name__)

class PostgresManager:
    def __init__(self):
        """Initialize the database service with environment variables"""
        if "PGHOST" in os.environ:
            self.host = os.environ["PGHOST"]
            logger.info(f"Using database host '{self.host}' from environment variable 'PGHOST'")
        else:
            self.host = "localhost"
            logger.warning(f"Using database host '{self.host}' since 'PGHOST' not set")
        
        if "PGPORT" in os.environ:
            self.port = int(os.environ["PGPORT"])
            logger.info(f"Using database port '{self.port}' from environment variable 'PGPORT'")
        else:
            self.port = 5432
            logger.warning(f"Using database port '{self.port}' since 'PGPORT' not set")
        
        if "PGUSER" in os.environ:
            self.user = os.environ["PGUSER"]
            logger.info(f"Using database user '{self.user}' from environment variable 'PGUSER'")
        else:
            self.user = "root"
            logger.warning(f"Using database user '{self.user}' since 'PGUSER' not set")
        
        if "PGPASSWORD" in os.environ:
            self.password = os.environ["PGPASSWORD"]
            logger.info("Using database password from environment variable 'PGPASSWORD'")
        else:
            raise ValueError("Environment variable 'PGPASSWORD' not set")

        if "PGDATABASE" in os.environ:
            self.db_name = os.environ["PGDATABASE"]
            logger.info(f"Using database name '{self.db_name}' from environment variable 'PGDATABASE'")
        else:
            self.db_name = "auth"
            logger.warning(f"Using database name '{self.db_name}' since 'PGDATABASE' not set")

        if "PGBACKUPDIR" in os.environ:
            self.backup_dir = os.environ["PGBACKUPDIR"]
            logger.info(f"Using backup directory '{self.backup_dir}' from environment variable 'PGBACKUPDIR'")
        else:
            self.backup_dir = "/tmp"
            logger.warning(f"Using backup directory '{self.backup_dir}' since 'PGBACKUPDIR' not set")

        logger.info("PostgresManager initialized")


    def pg_dump(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_file = os.path.join(self.backup_dir, f"{self.db_name}_{timestamp}.dump")

        logger.info(f"Starting backup for database '{self.db_name}'...")

        try:
            # -F c: Custom format (compressed) as recommended
            # -f: output file
            command = [
                "pg_dump",
                "-h", self.host,
                "-p", str(self.port),
                "-U", self.user,
                "-F", "c",
                "-f", backup_file,
                self.db_name
            ]

            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"Backup saved to '{backup_file}'")
            
            self.verify_backup(backup_file)
            
            return backup_file

        except subprocess.CalledProcessError as e:
            logger.error(f"Error running pg_dump: {e.stderr}")
            raise


    def verify_backup(self, backup_file):
        logger.info(f"Verifying backup '{backup_file}'...")
        try:
            # pg_restore -l lists the TOC. If the file is corrupt or not a dump, it fails.
            subprocess.run(
                ["pg_restore", "-l", backup_file],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            logger.info("Backup verification successful.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Backup verification failed: {e.stderr.decode()}")
            raise


    def restore_backup(self, backup_file):
        logger.info(f"Restoring backup from '{backup_file}'...")
        try:
            # -d: Connect to 'postgres' (maintenance db) initially
            # -C: Create the target database (name from dump file) before restoring
            # -c: Drop the database before creating it (when combined with -C)
            # --if-exists: used with -c to silently ignore 'does not exist' errors
            command = [
                "pg_restore",
                "-h", self.host,
                "-p", str(self.port),
                "-U", self.user,
                "-d", "postgres",
                "-C",
                "-c",
                "--if-exists",
                backup_file
            ]

            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"Backup restored successfully from '{backup_file}'")

        except subprocess.CalledProcessError as e:
            logger.error(f"Error restoring backup: {e.stderr}")
            raise


            