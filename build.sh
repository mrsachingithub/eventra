#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Run migrations (ensure database URL is set in Render env vars)
python -m flask db upgrade
