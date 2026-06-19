#!/usr/bin/env bash

set -e

if [ ! -d ".venv" ]; then
    echo "Errore: ambiente virtuale non trovato. Eseguire prima ./install.sh"
    exit 1
fi

.venv/bin/python manage.py runserver
