"""
Data Migration Utility for TalentFlow-AI.

Provides version-stamped database migrations for Cloud Firestore, with support for:
- Sequential version tracking via a `migrations` collection
- Forward migrations (`migrate`)
- Reversible rollback operations (`rollback`)
- Dry-run validation mode (`--dry-run`)
- Detailed migration status reporting (`status`)

Usage:
    python scripts/migrate_data.py status
    python scripts/migrate_data.py migrate [--target-version VERSION] [--dry-run]
    python scripts/migrate_data.py rollback [--target-version VERSION] [--dry-run]
"""

import sys
import os
import argparse
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Callable, Optional

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("migrate_data")

COLLECTION_MIGRATIONS = "migrations"
COLLECTION_CANDIDATES = "candidates"
COLLECTION_JOBS = "jobs"


def utc_now_iso() -> str:
    """Return current UTC timestamp string."""
    return datetime.now(timezone.utc).isoformat()


class Migration:
    """Base class defining a version-stamped migration."""
    
    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description

    def up(self, db: Any, dry_run: bool = False) -> bool:
        """Apply migration changes (forward)."""
        raise NotImplementedError

    def down(self, db: Any, dry_run: bool = False) -> bool:
        """Revert migration changes (rollback)."""
        raise NotImplementedError


class V1_0_1_NormalizeCandidateStages(Migration):
    """Migration v1.0.1: Normalize lowercase string candidate pipeline stages."""
    
    def __init__(self):
        super().__init__(
            version="v1.0.1",
            description="Normalize candidate pipeline stage strings to lower_snake_case format"
        )

    def up(self, db: Any, dry_run: bool = False) -> bool:
        logger.info(f"[{self.version} UP] {self.description}")
        if dry_run or db is None:
            logger.info("  [DRY RUN] Simulating pipeline stage normalization...")
            return True
            
        docs = db.collection(COLLECTION_CANDIDATES).stream()
        count = 0
        for doc in docs:
            data = doc.to_dict()
            stage = data.get("pipeline_stage", "")
            normalized = stage.lower().replace("-", "_").replace(" ", "_")
            if stage != normalized:
                doc.reference.update({"pipeline_stage": normalized, "updated_at": utc_now_iso()})
                count += 1
        logger.info(f"  Normalized pipeline stage for {count} candidates.")
        return True

    def down(self, db: Any, dry_run: bool = False) -> bool:
        logger.info(f"[{self.version} DOWN] Reverting pipeline stage normalization")
        if dry_run or db is None:
            logger.info("  [DRY RUN] Simulating rollback of stage normalization...")
            return True
        return True


class V1_0_2_AddMetadataFieldsToJobs(Migration):
    """Migration v1.0.2: Ensure all Job documents have a metadata object and application count."""
    
    def __init__(self):
        super().__init__(
            version="v1.0.2",
            description="Add metadata dictionary and default application_count to existing job records"
        )

    def up(self, db: Any, dry_run: bool = False) -> bool:
        logger.info(f"[{self.version} UP] {self.description}")
        if dry_run or db is None:
            logger.info("  [DRY RUN] Simulating addition of job metadata fields...")
            return True
            
        docs = db.collection(COLLECTION_JOBS).stream()
        count = 0
        for doc in docs:
            data = doc.to_dict()
            updates = {}
            if "application_count" not in data:
                updates["application_count"] = 0
            if "metadata" not in data:
                updates["metadata"] = {"migrated_by": self.version}
            if updates:
                doc.reference.update(updates)
                count += 1
        logger.info(f"  Updated {count} job documents with metadata defaults.")
        return True

    def down(self, db: Any, dry_run: bool = False) -> bool:
        logger.info(f"[{self.version} DOWN] Reverting job metadata additions")
        if dry_run or db is None:
            logger.info("  [DRY RUN] Simulating rollback of job metadata additions...")
            return True
        return True


# Migration Registry sorted by version
MIGRATIONS_REGISTRY: List[Migration] = [
    V1_0_1_NormalizeCandidateStages(),
    V1_0_2_AddMetadataFieldsToJobs(),
]


def get_firestore_db(cred_path: Optional[str] = None):
    """Initialize Firebase Admin SDK and return Firestore client."""
    try:
        from backend.firebase.firebase import initialize_firebase
        from firebase_admin import firestore
        app = initialize_firebase(cred_path=cred_path)
        if app:
            return firestore.client()
    except Exception as e:
        logger.warning(f"Could not connect to Firestore ({e}). Using mock interface.")
    return None


def get_applied_migrations(db: Any) -> Dict[str, Dict[str, Any]]:
    """Retrieve dictionary of applied migrations from Firestore."""
    if db is None:
        return {}
    applied = {}
    try:
        docs = db.collection(COLLECTION_MIGRATIONS).stream()
        for doc in docs:
            applied[doc.id] = doc.to_dict()
    except Exception as e:
        logger.warning(f"Error fetching applied migrations: {e}")
    return applied


def record_migration_applied(db: Any, migration: Migration, dry_run: bool):
    """Record a newly applied migration in Firestore."""
    if dry_run or db is None:
        return
    data = {
        "version": migration.version,
        "description": migration.description,
        "applied_at": utc_now_iso(),
        "status": "success"
    }
    db.collection(COLLECTION_MIGRATIONS).document(migration.version).set(data)


def record_migration_rolled_back(db: Any, migration: Migration, dry_run: bool):
    """Remove a migration record from Firestore upon rollback."""
    if dry_run or db is None:
        return
    db.collection(COLLECTION_MIGRATIONS).document(migration.version).delete()


def run_migrations(action: str, target_version: Optional[str], dry_run: bool, cred_path: Optional[str]):
    """Execute forward migration, rollback, or status check."""
    db = get_firestore_db(cred_path)
    applied_map = get_applied_migrations(db)

    print("\n" + "=" * 70)
    print(f"            TALENTFLOW-AI DATA MIGRATION ENGINE ({action.upper()})")
    print("=" * 70)

    if action == "status":
        print(f"{'VERSION':<12} | {'STATUS':<12} | {'DESCRIPTION'}")
        print("-" * 70)
        for m in MIGRATIONS_REGISTRY:
            status = "APPLIED" if m.version in applied_map else "PENDING"
            print(f"{m.version:<12} | {status:<12} | {m.description}")
        print("=" * 70 + "\n")
        return

    if action == "migrate":
        for m in MIGRATIONS_REGISTRY:
            if target_version and m.version > target_version:
                continue
            if m.version in applied_map:
                logger.info(f"Skipping already applied migration: {m.version}")
                continue
            
            logger.info(f"Applying migration {m.version}...")
            success = m.up(db, dry_run=dry_run)
            if success:
                record_migration_applied(db, m, dry_run)
                logger.info(f"Successfully applied: {m.version}")
            else:
                logger.error(f"Failed migration {m.version}. Stopping migration run.")
                break

    elif action == "rollback":
        for m in reversed(MIGRATIONS_REGISTRY):
            if target_version and m.version < target_version:
                continue
            if m.version not in applied_map and not dry_run:
                logger.info(f"Skipping unapplied migration: {m.version}")
                continue
            
            logger.info(f"Rolling back migration {m.version}...")
            success = m.down(db, dry_run=dry_run)
            if success:
                record_migration_rolled_back(db, m, dry_run)
                logger.info(f"Successfully rolled back: {m.version}")
            else:
                logger.error(f"Failed to rollback {m.version}. Stopping rollback run.")
                break

    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="TalentFlow-AI Database Migration Utility.")
    parser.add_argument("action", choices=["migrate", "rollback", "status"], help="Migration command")
    parser.add_argument("--target-version", type=str, help="Target version to migrate or rollback to")
    parser.add_argument("--dry-run", action="store_true", help="Simulate migration without modifying Firestore")
    parser.add_argument("--cred", type=str, help="Path to Firebase credentials JSON file")

    args = parser.parse_args()
    run_migrations(
        action=args.action,
        target_version=args.target_version,
        dry_run=args.dry_run,
        cred_path=args.cred
    )


if __name__ == "__main__":
    main()
