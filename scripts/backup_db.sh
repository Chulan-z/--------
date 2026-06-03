#!/usr/bin/env bash
set -euo pipefail

DATABASE_URL="${DATABASE_URL:-postgresql://news:news@localhost:5432/newsdb}"
BACKUP_DIR="${BACKUP_DIR:-backups}"
mkdir -p "$BACKUP_DIR"
FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).dump"
pg_dump -Fc "$DATABASE_URL" -f "$FILE"
echo "Backup created: $FILE"
