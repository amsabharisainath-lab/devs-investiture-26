#!/bin/bash
set -e

DATE=$(date +"%Y-%m-%d_%H-%M")
ARCHIVE="mongo_backup_$DATE.gz"

echo "Starting MongoDB backup..."

mongodump \
  --uri="$MONGO_URI" \
  --archive="$ARCHIVE" \
  --gzip

echo "Uploading to Google Drive..."

rclone copy "$ARCHIVE" gdrive:mongo_backups/

echo "Backup completed successfully"
curl -d "Backup successful" ntfy.sh/${NTFY_TOPIC}
