#!/bin/bash
# StemScribe — one-shot setup and run

set -e

echo "==> Installing Django..."
pip install -r requirements.txt --quiet

echo "==> Running migrations..."
python manage.py migrate --run-syncdb

echo "==> Starting server..."
echo ""
echo "  Open: http://127.0.0.1:8000"
echo "  Student login:  student@imperial.ac.uk / demo1234"
echo "  Teacher login:  teacher@imperial.ac.uk / demo1234"
echo ""
echo "  Set ANTHROPIC_API_KEY for live AI analysis."
echo ""

python manage.py runserver
