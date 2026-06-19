#!/usr/bin/env bash

set -e

echo "=========================================="
echo " Installazione Progetto 2 - Servizio Sanitario"
echo "=========================================="

if command -v python3.12 >/dev/null 2>&1; then
    PYTHON_CMD="python3.12"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
else
    echo "Errore: Python non trovato. Installare Python 3.12 o Python 3."
    exit 1
fi

echo "Uso interprete Python: $PYTHON_CMD"

if [ ! -f "manage.py" ]; then
    echo "Errore: manage.py non trovato. Eseguire lo script dalla cartella principale del progetto."
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "Errore: requirements.txt non trovato."
    exit 1
fi

if [ ! -f "data/my_serviziosanitariounibg.ods" ]; then
    echo "Errore: file data/my_serviziosanitariounibg.ods non trovato."
    exit 1
fi

echo "Creazione ambiente virtuale..."
$PYTHON_CMD -m venv .venv

echo "Installazione dipendenze..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

echo "Creazione/Aggiornamento database SQLite..."
.venv/bin/python manage.py migrate

echo "Importazione dati iniziali da ODS..."
.venv/bin/python manage.py import_ods

echo "=========================================="
echo " Installazione completata con successo."
echo ""
echo "Per avviare il progetto:"
echo "source .venv/bin/activate"
echo "python manage.py runserver"
echo ""
echo "Poi aprire:"
echo "http://127.0.0.1:8000/"
echo "=========================================="
