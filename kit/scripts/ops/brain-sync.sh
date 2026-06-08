#!/bin/bash
# Brain Sync — Bidirectional (Hetzner ↔ Mac Mini)
# Hetzner = master for conflicts. Both sides can write.
# Every 30 min via cron.

REMOTE="mafalda@100.127.229.52"
LOCAL="/root/aurelio-v2/brain/"
REMOTE_PATH="/Users/Shared/laagam-brain/"
LOG="/var/log/brain-sync.log"

RSYNC_OPTS="-avz --update --timeout=30 --include=*/ --include=*.md --include=*.json --include=*.txt --include=*.yaml --exclude=* --exclude=credentials/"

echo "$(date -Iseconds) — Brain sync starting" >> "$LOG"

# 1. Pull from Mac Mini → Hetzner (agent writes)
rsync $RSYNC_OPTS "${REMOTE}:${REMOTE_PATH}knowledge/" "${LOCAL}knowledge/" >> "$LOG" 2>&1

# 2. Push Hetzner → Mac Mini (Aurelio writes, master)
rsync $RSYNC_OPTS "${LOCAL}knowledge/" "${REMOTE}:${REMOTE_PATH}knowledge/" >> "$LOG" 2>&1
rsync $RSYNC_OPTS "${LOCAL}templates/" "${REMOTE}:${REMOTE_PATH}templates/" >> "$LOG" 2>&1
rsync $RSYNC_OPTS "${LOCAL}brand/" "${REMOTE}:${REMOTE_PATH}brand/" >> "$LOG" 2>&1

STATUS=$?
echo "$(date -Iseconds) — Brain sync finished (exit: $STATUS)" >> "$LOG"
