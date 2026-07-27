# MD Banking Manager

Der MD Banking Manager ist eine Flask-Webanwendung zur Verwaltung von selbst angelegten Finanzkonten und Buchungen. Es besteht keine Verbindung zu einer echten Bank.

Das Projekt wurde im Web- und Datenbankenpraktikum im Sommersemester 2026 von Dhruvit Goti und Milad Orifien erstellt.

## Funktionen

- Registrierung, Anmeldung und Abmeldung
- mehrere Finanzkonten pro Benutzer
- Buchungen manuell anlegen
- Buchungen suchen, filtern und sortieren
- Kategorien und Schlagwörter verwalten
- automatische Zuordnung von Buchungen zu Kategorien
- Excel-Import und Excel-Export
- Auswertung nach Zeitraum und Kategorie
- Gruppen und Nachrichten
- Profildaten und Passwort ändern

## Projektaufbau

```text
app.py            Start der Flask-Anwendung
config.py         Einstellungen und Datenbankzugang
database/         Datenbankverbindung und SQL-Schema
repositories/     SQL-Abfragen
services/         Verarbeitung und Validierung
routes/           Flask-Routen
templates/        HTML-Seiten
static/           CSS und JavaScript
examples/         Beispieldatei für den Excel-Import
```

Die Anwendung ist in Routen, Services und Repositories aufgeteilt. Dadurch bleiben Oberfläche, Verarbeitung und Datenbankzugriff voneinander getrennt.

## Einrichtung

### 1. Virtuelle Umgebung erstellen

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Einstellungen anlegen

```bash
cp .env.example .env
```

Anschließend müssen in `.env` das eigene PostgreSQL-Passwort und ein eigener `APP_SECRET_KEY` eingetragen werden. Über `FLASK_PORT` kann bei Bedarf der lokale Port der Webanwendung geändert werden.

### 3. Datenbank vorbereiten

```bash
python init_db.py
```

Dabei werden die Tabellen neu erstellt und mit fiktiven Demodaten gefüllt. Vorhandene Projektdaten werden dabei gelöscht.

### 4. Anwendung starten

```bash
python app.py
```

Die Anwendung ist standardmäßig unter folgender Adresse erreichbar:

```text
http://127.0.0.1:5001
```

## Demo-Zugang

```text
E-Mail: anna.mueller@example.com
Passwort: AnnaTest!123
```

## Excel-Import

Die Excel-Datei benötigt diese Spalten:

```text
Wertstellung | Betrag | Empfänger | Verwendungszweck
```

Eine Beispieldatei liegt unter `examples/beispiel_import.xlsx`.

## Abgabehinweis

Die lokale `.env`, die virtuelle Umgebung und PyCharm-Dateien gehören nicht in die Abgabe. Der aktuelle SQL-Dump liegt unter `database/`, die UML-Diagramme unter `docs/`.
