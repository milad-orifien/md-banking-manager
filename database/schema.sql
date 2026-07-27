DROP TABLE IF EXISTS nachricht CASCADE;
DROP TABLE IF EXISTS gruppeneinladung CASCADE;
DROP TABLE IF EXISTS gruppenmitglied CASCADE;
DROP TABLE IF EXISTS benutzergruppe CASCADE;
DROP TABLE IF EXISTS kontoeintrag CASCADE;
DROP TABLE IF EXISTS schlagwort CASCADE;
DROP TABLE IF EXISTS kategorie CASCADE;
DROP TABLE IF EXISTS konto CASCADE;
DROP TABLE IF EXISTS passwort CASCADE;
DROP TABLE IF EXISTS kunde CASCADE;

CREATE TABLE kunde (
    kundenid SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    vorname VARCHAR(50) NOT NULL,
    nachname VARCHAR(100) NOT NULL,
    alter INTEGER CHECK (alter IS NULL OR alter BETWEEN 1 AND 119),
    bankinstitut VARCHAR(100),
    erstellt_am TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE passwort (
    kundenid INTEGER PRIMARY KEY REFERENCES kunde(kundenid) ON DELETE CASCADE,
    passwort_hash TEXT NOT NULL
);

CREATE TABLE konto (
    kontoid SERIAL PRIMARY KEY,
    kundenid INTEGER NOT NULL REFERENCES kunde(kundenid) ON DELETE CASCADE,
    kontoname VARCHAR(100) NOT NULL,
    erstellt_am TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (kundenid, kontoname)
);

CREATE TABLE kategorie (
    kategorieid SERIAL PRIMARY KEY,
    kundenid INTEGER NOT NULL REFERENCES kunde(kundenid) ON DELETE CASCADE,
    bezeichnung VARCHAR(80) NOT NULL,
    ist_standard BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (kundenid, bezeichnung)
);

CREATE TABLE schlagwort (
    schlagwortid SERIAL PRIMARY KEY,
    kategorieid INTEGER NOT NULL REFERENCES kategorie(kategorieid) ON DELETE CASCADE,
    wort VARCHAR(100) NOT NULL,
    UNIQUE (kategorieid, wort)
);

CREATE TABLE kontoeintrag (
    eintragid SERIAL PRIMARY KEY,
    kontoid INTEGER NOT NULL REFERENCES konto(kontoid) ON DELETE CASCADE,
    kategorieid INTEGER REFERENCES kategorie(kategorieid) ON DELETE SET NULL,
    wertstellungsdatum TIMESTAMP NOT NULL,
    betrag NUMERIC(12, 2) NOT NULL CHECK (betrag <> 0),
    empfaenger VARCHAR(200) NOT NULL,
    verwendungszweck TEXT NOT NULL,
    erstellt_am TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE benutzergruppe (
    gruppenid SERIAL PRIMARY KEY,
    gruppenname VARCHAR(100) NOT NULL,
    erstellt_von INTEGER NOT NULL REFERENCES kunde(kundenid) ON DELETE CASCADE,
    erstellt_am TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE gruppenmitglied (
    gruppenid INTEGER NOT NULL REFERENCES benutzergruppe(gruppenid) ON DELETE CASCADE,
    kundenid INTEGER NOT NULL REFERENCES kunde(kundenid) ON DELETE CASCADE,
    beigetreten_am TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (gruppenid, kundenid)
);

CREATE TABLE gruppeneinladung (
    einladungid SERIAL PRIMARY KEY,
    gruppenid INTEGER NOT NULL REFERENCES benutzergruppe(gruppenid) ON DELETE CASCADE,
    erstellt_von INTEGER NOT NULL REFERENCES kunde(kundenid) ON DELETE CASCADE,
    empfaengerid INTEGER NOT NULL REFERENCES kunde(kundenid) ON DELETE CASCADE,
    token VARCHAR(100) NOT NULL UNIQUE,
    angenommen BOOLEAN NOT NULL DEFAULT FALSE,
    erstellt_am TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE nachricht (
    nachrichtid SERIAL PRIMARY KEY,
    absenderid INTEGER NOT NULL REFERENCES kunde(kundenid) ON DELETE CASCADE,
    empfaengerid INTEGER NOT NULL REFERENCES kunde(kundenid) ON DELETE CASCADE,
    betreff VARCHAR(150) NOT NULL,
    inhalt TEXT NOT NULL,
    einladungid INTEGER REFERENCES gruppeneinladung(einladungid) ON DELETE SET NULL,
    gelesen BOOLEAN NOT NULL DEFAULT FALSE,
    gesendet_am TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_konto_kundenid ON konto(kundenid);
CREATE INDEX idx_eintrag_konto_datum ON kontoeintrag(kontoid, wertstellungsdatum DESC);
CREATE INDEX idx_kategorie_kundenid ON kategorie(kundenid);
CREATE INDEX idx_schlagwort_kategorieid ON schlagwort(kategorieid);
CREATE INDEX idx_gruppenmitglied_kundenid ON gruppenmitglied(kundenid);
CREATE INDEX idx_nachricht_empfaenger ON nachricht(empfaengerid, gesendet_am DESC);

-- Groß- und Kleinschreibung sollen bei diesen sichtbaren Bezeichnungen
-- keine inhaltlich doppelten Datensätze erzeugen.
CREATE UNIQUE INDEX uq_kunde_email_ci ON kunde (LOWER(email));
CREATE UNIQUE INDEX uq_kategorie_kunde_name_ci ON kategorie (kundenid, LOWER(bezeichnung));
CREATE UNIQUE INDEX uq_schlagwort_kategorie_wort_ci ON schlagwort (kategorieid, LOWER(wort));
