# Workflow: Finanzgericht-Entscheidungen überwachen

## Ziel
Täglich neue Urteile und Entscheidungen der deutschen Finanzgerichte automatisch erfassen und per E-Mail an das Team melden.

## Eingaben (Inputs)
- `state.json` — Zustand des letzten Laufs (bereits gesehene Entscheidungs-IDs pro Gericht)
- Umgebungsvariablen (GitHub Secrets):
  - `GMAIL_ADDRESS` — Absender-E-Mail
  - `GMAIL_APP_PASSWORD` — Gmail App-Passwort
  - `NOTIFICATION_EMAIL` — Empfänger (kommagetrennt)

## Ablauf
1. `main.py` lädt `state.json`
2. Für jedes aktivierte Gericht in `courts_config.py`: Scraper ausführen
3. Neue Entscheidungen (nicht in `state.json`) identifizieren
4. `state.json` aktualisieren und speichern
5. Falls neue Entscheidungen vorhanden: E-Mail-Digest versenden
6. GitHub Actions committet `state.json` zurück ins Repository

## Scraper-Typen

| Typ | Gerichte | Technologie |
|---|---|---|
| `voris` | FG Niedersachsen | requests + BeautifulSoup (kein Browser) |
| `juris` | BW, Berlin, Hamburg, Hessen, MV, RLP, Sachsen-Anhalt | Playwright (Chromium, headless) |
| `bayern` | FG München / Nürnberg | Playwright (Chromium, headless) |
| `nrw` | FG Köln / Düsseldorf / Münster | Playwright (Chromium, headless) |
| `stub` | Bremen, Saarland, Sachsen, SH, Thüringen | Deaktiviert — gibt leere Liste zurück |

## Bekannte Einschränkungen

| Gericht | Problem | Lösung |
|---|---|---|
| FG Bremen | Nur über Juris (kostenpflichtig) | Manuell prüfen |
| FG Saarland | Cloudflare WAF blockiert Scraper | Manuell prüfen: saarland.de/fgds |
| FG Sachsen | Kein FG im esamosplus-Portal | Keine öffentliche DB bekannt |
| FG Schleswig-Holstein | URL fehlt | URL ergänzen, dann `scraper_type: juris` setzen |
| FG Thüringen | URL fehlt | URL ergänzen, dann `scraper_type: juris` setzen |
| Zeitverschiebung | Cron läuft 06:00 UTC = 07:00 CET / 08:00 CEST | Saisonale Abweichung von 1 Stunde im Sommer |

## Fehlerbehandlung
- Jedes Gericht wird in einem eigenen `try/except`-Block ausgeführt
- Ein Fehler bei einem Gericht stoppt nicht die anderen
- Fehlermeldungen erscheinen im GitHub Actions Log
- E-Mail-Versandsfehler → Exit-Code 1 (GitHub Actions markiert den Run als fehlgeschlagen)

## Neues Gericht hinzufügen
1. URL des Gerichts in `finanzgerichte.md` eintragen
2. In `courts_config.py`: neuen `CourtConfig`-Eintrag hinzufügen
   - `enabled=True`
   - Passenden `scraper_type` wählen (meist `juris` für Landesrecht-Portale)
   - `base_url` in `config` setzen
3. Testen: `python main.py` lokal ausführen und Ausgabe prüfen
4. Wenn nötig: CSS-Selektoren im Scraper anpassen (Browser-DevTools auf der Seite öffnen)

## CSS-Selektoren für Juris-Portale warten
Falls ein juris-Portal keine Ergebnisse mehr liefert (nach UI-Update):
1. Portal in Chrome öffnen
2. DevTools → Inspector: Ergebnis-Element inspizieren
3. Passenden Selektor in `juris_scraper.py` → `_wait_for_results()` Kandidatenliste ergänzen
4. In `monitor_courts.md` dokumentieren

## Ausgabe (Output)
**E-Mail-Digest** (wird nur versendet, wenn neue Entscheidungen vorhanden):

```
Neue Finanzgericht-Entscheidungen — 18.03.2026

─── FG Niedersachsen (2) ───
• 17.03.2026 — 2 K 152/25 — Umsatzsteuer bei Photovoltaikanlagen
  https://voris.wolterskluwer-online.de/browse/document/bf62126d-...

─── FG Baden-Württemberg (1) ───
• 16.03.2026 — 1 K 100/25 — Körperschaftsteuer
  https://www.landesrecht-bw.de/bsbw/document/JURE260001234

Gesamt: 3 neue Entscheidungen aus 2 Gerichten
Abruf: 18.03.2026 07:02:34 CET
```

## Manuell ausführen (lokal)
```bash
# Abhängigkeiten installieren
pip install -r requirements.txt
playwright install chromium

# Umgebungsvariablen setzen (oder in .env eintragen)
export GMAIL_ADDRESS="fg-monitor@gmail.com"
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
export NOTIFICATION_EMAIL="kollege@firma.de"

# Agent ausführen
python main.py
```

## Manuell in GitHub Actions auslösen
1. GitHub → Repository → Actions → "Monitor German Tax Courts"
2. "Run workflow" → Branch `main` → "Run workflow"
