#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Run migrations (ensure database URL is set in Render env vars)
# Generate migration if changes detected (or initial run)
python -m flask db migrate -m "Auto-generated migration" || true
python -m flask db upgrade
