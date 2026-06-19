from django.core.management.base import BaseCommand
from pathlib import Path
from decimal import Decimal
from datetime import date
import zipfile
import re
import html

from ricoveri.models import (
    Cittadino,
    Ospedale,
    Patologia,
    PatologiaCronica,
    PatologiaMortale,
    Ricovero,
    PatologiaRicovero,
)


class Command(BaseCommand):
    help = "Importa i dati iniziali dal file ODS nella base dati SQLite"

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parents[3]
        ods_path = base_dir / "data" / "my_serviziosanitariounibg.ods"

        if not ods_path.exists():
            self.stderr.write(self.style.ERROR(f"File non trovato: {ods_path}"))
            return

        sheets = self.read_ods(ods_path)

        self.import_cittadini(sheets.get("Cittadino", []))
        self.import_ospedali(sheets.get("Ospedali", []))
        self.import_patologie(sheets.get("Patologia", []))
        self.import_patologie_croniche(sheets.get("PatologiaCronica", []))
        self.import_patologie_mortali(sheets.get("PatologiaMortale", []))
        self.import_ricoveri(sheets.get("Ricovero", []))
        self.import_patologie_ricoveri(sheets.get("PatologiaRicovero", []))

        self.stdout.write(self.style.SUCCESS("Importazione completata."))

    def read_ods(self, ods_path):
        with zipfile.ZipFile(ods_path, "r") as ods:
            content = ods.read("content.xml").decode("utf-8", errors="ignore")

        sheets = {}

        table_pattern = re.compile(
            r'<table:table[^>]*table:name="([^"]+)"[^>]*>(.*?)</table:table>',
            re.DOTALL
        )

        row_pattern = re.compile(
            r"<table:table-row[^>]*>(.*?)</table:table-row>",
            re.DOTALL
        )

        cell_pattern = re.compile(
            r"<table:table-cell([^>]*)>(.*?)</table:table-cell>",
            re.DOTALL
        )

        for sheet_name, table_content in table_pattern.findall(content):
            rows = []

            for row_content in row_pattern.findall(table_content):
                row = []

                for cell_attrs, cell_content in cell_pattern.findall(row_content):
                    repeat_match = re.search(
                        r'table:number-columns-repeated="(\d+)"',
                        cell_attrs
                    )

                    repeat = int(repeat_match.group(1)) if repeat_match else 1
                    value = self.extract_cell_value(cell_attrs, cell_content)

                    for _ in range(repeat):
                        row.append(value)

                if any(str(c).strip() for c in row):
                    rows.append(row)

            sheets[sheet_name] = rows

        return sheets

    def extract_cell_value(self, attrs, content):
        date_match = re.search(r'office:date-value="([^"]+)"', attrs)
        if date_match:
            return date.fromisoformat(date_match.group(1))

        value_match = re.search(r'office:value="([^"]+)"', attrs)
        if value_match:
            return value_match.group(1)

        text_parts = re.findall(r"<text:p[^>]*>(.*?)</text:p>", content, re.DOTALL)
        text = " ".join(text_parts)

        text = re.sub(r"<[^>]+>", "", text)
        text = html.unescape(text).strip()

        return text

    def import_cittadini(self, rows):
        count = 0

        for r in rows:
            if len(r) < 6:
                continue

            Cittadino.objects.update_or_create(
                CSSN=r[0],
                defaults={
                    "nome": r[1],
                    "cognome": r[2],
                    "dataNascita": r[3],
                    "luogoNascita": r[4],
                    "indirizzo": r[5],
                }
            )

            count += 1

        self.stdout.write(f"Cittadini importati: {count}")

    def import_ospedali(self, rows):
        count = 0

        for r in rows:
            if len(r) < 7:
                continue

            Ospedale.objects.update_or_create(
                codOspedale=r[0],
                defaults={
                    "nome": r[1],
                    "citta": r[2],
                    "indirizzo": r[3],
                    "dirSanitario": r[4],
                    "latitudine": Decimal(str(r[5])),
                    "longitudine": Decimal(str(r[6])),
                }
            )

            count += 1

        self.stdout.write(f"Ospedali importati: {count}")

    def import_patologie(self, rows):
        count = 0

        for r in rows:
            if len(r) < 3:
                continue

            Patologia.objects.update_or_create(
                codPatologia=r[0],
                defaults={
                    "nome": r[1],
                    "livello_rischio": r[2],
                }
            )

            count += 1

        self.stdout.write(f"Patologie importate: {count}")

    def import_patologie_croniche(self, rows):
        count = 0

        for r in rows:
            if len(r) < 1:
                continue

            try:
                patologia = Patologia.objects.get(codPatologia=r[0])
                PatologiaCronica.objects.update_or_create(
                    patologia=patologia
                )
                count += 1
            except Patologia.DoesNotExist:
                self.stderr.write(f"Patologia cronica non trovata: {r[0]}")

        self.stdout.write(f"Patologie croniche importate: {count}")

    def import_patologie_mortali(self, rows):
        count = 0

        for r in rows:
            if len(r) < 1:
                continue

            try:
                patologia = Patologia.objects.get(codPatologia=r[0])
                PatologiaMortale.objects.update_or_create(
                    patologia=patologia
                )
                count += 1
            except Patologia.DoesNotExist:
                self.stderr.write(f"Patologia mortale non trovata: {r[0]}")

        self.stdout.write(f"Patologie mortali importate: {count}")

    def import_ricoveri(self, rows):
        count = 0

        for r in rows:
            if len(r) < 7:
                continue

            try:
                ospedale = Ospedale.objects.get(codOspedale=r[0])
                cittadino = Cittadino.objects.get(CSSN=r[2])

                Ricovero.objects.update_or_create(
                    codRicovero=r[1],
                    defaults={
                        "ospedale": ospedale,
                        "cittadino": cittadino,
                        "data": r[3],
                        "durata": Decimal(str(r[4])),
                        "diagnosi": r[5],
                        "costo": Decimal(str(r[6])),
                    }
                )

                count += 1

            except Ospedale.DoesNotExist:
                self.stderr.write(f"Ospedale non trovato: {r[0]}")

            except Cittadino.DoesNotExist:
                self.stderr.write(f"Cittadino non trovato: {r[2]}")

        self.stdout.write(f"Ricoveri importati: {count}")

    def import_patologie_ricoveri(self, rows):
        count = 0

        for r in rows:
            if len(r) < 2:
                continue

            try:
                ricovero = Ricovero.objects.get(codRicovero=r[0])
                patologia = Patologia.objects.get(codPatologia=r[1])

                PatologiaRicovero.objects.update_or_create(
                    ricovero=ricovero,
                    patologia=patologia
                )

                count += 1

            except Ricovero.DoesNotExist:
                self.stderr.write(f"Ricovero non trovato: {r[0]}")

            except Patologia.DoesNotExist:
                self.stderr.write(f"Patologia non trovata: {r[1]}")

        self.stdout.write(f"Patologie ricoveri importate: {count}")
