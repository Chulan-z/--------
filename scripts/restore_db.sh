#!/usr/bin/env bash
set -euo pipefail

if [ "${1:-}" = "" ]; then
  echo "Usage: scripts/restore_db.sh backups/backup_YYYYMMDD_HHMMSS.dump"
  exit 1
fi

DATABASE_URL="${DATABASE_URL:-postgresql://news:news@localhost:5432/newsdb}"
pg_restore --clean --if-exists -d "$DATABASE_URL" "$1"
echo "Database restored from: $1"
