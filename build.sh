#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Run migrations (ensure database URL is set in Render env vars)
# Force cleanup of old validation history (resolves "Can't locate revision")
python -c "import os, psycopg2; from urllib.parse import urlparse; url=urlparse(os.environ.get('DATABASE_URL')); conn=psycopg2.connect(dbname=url.path[1:], user=url.username, password=url.password, host=url.hostname); cur=conn.cursor(); cur.execute('DROP TABLE IF EXISTS alembic_version_old, alembic_version'); conn.commit();" || true

# Generate migration if changes detected (or initial run)
python -m flask db migrate -m "Auto-generated migration" || true
python -m flask db upgrade
