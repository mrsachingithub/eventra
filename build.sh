#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Run migrations (only apply existing valid migrations)
python -m flask db upgrade
python create_admin.py
