# Workflow: Steuer-News von Beratungs- und Anwaltsgesellschaften überwachen

## Ziel
Wöchentlich die offiziellen News-/Blog-/Insights-Seiten der relevanten Beratungs-
und Kanzleimarken (JUVE Top30) auf neue Steuer-/Recht-/Wirtschafts-Beiträge prüfen
und einen markdown-Bericht ins Repository commiten.

## Eingaben (Inputs)
- `companies_config.py` — Liste der überwachten Unternehmen inkl. CSS-Selektoren
  pro Unternehmen (Quelle: `Steuernews_Links_02042026.xlsx`, Sheet *JUVE Top30 2025*)
- `state.json` — bereits gesehene Artikel-URLs pro Unternehmen

## Architektur (WAT)
- **Workflow:** dieses Dokument
- **Agent:** `main.py` orchestriert: State laden → Seite holen → Selektoren anwenden → Diff → State speichern → Report schreiben
- **Tools:**
  - `tools/fetch_page.py` — HTTP-Fetcher (requests + Retries, realistischer User-Agent)
  - `tools/scrape_articles.py` — generischer Selector-basierter Extractor (BeautifulSoup) inkl. Datumsnormalisierung
  - `tools/write_report.py` — schreibt `LATEST_REPORT.md`

## Ablauf
1. `main.py` lädt `state.json`
2. Für jedes aktivierte Unternehmen in `companies_config.py` **mit hinterlegten Selektoren**:
   - URL abrufen (`tools/fetch_page.py`)
   - Mit den CSS-Selektoren des Unternehmens Artikel extrahieren (`tools/scrape_articles.py`)
   - Neue URLs (nicht in `state.json`) als Treffer markieren
   - Alle gesehenen URLs in `state.json` aktualisieren
3. Unternehmen mit `selectors=None` werden mit Hinweis im Log übersprungen
4. `state.json` speichern
5. Wenn Treffer vorhanden: `LATEST_REPORT.md` schreiben
6. GitHub Actions committed `state.json` (immer) und `LATEST_REPORT.md` (bei Treffern)

## Seed-Lauf (Erstlauf pro Unternehmen)
Beim ersten Lauf eines Unternehmens wird *kein* Bericht erstellt — alle gefundenen
Artikel werden nur als „gesehen" markiert. So vermeiden wir einen riesigen
Initial-Report bei neu hinzugefügten Unternehmen.

## Aktueller Stand (Pilot)
Folgende 9 Unternehmen haben Selektoren und liefern beim Smoke-Test echte Artikel:

| # | Unternehmen | Treffer im Smoke-Test | Datum / Summary |
|---|---|---:|---|
| 1 | EY | 3 | beides ✓ |
| 2 | KPMG | 27 | Summary ✓, Datum nur in JSON-Attributen (übersprungen) |
| 3 | PwC | 20 | beides ✓ |
| 4 | Deloitte | 6 | keine Datumsangaben im HTML |
| 6 | Flick Gocke Schaumburg | 4 | keine Datumsangaben im HTML |
| 7 | Rödl & Partner | 30 | Datum ✓ |
| 26 | KMLZ | 3 | beides ✓ |
| 27 | Dr. Kleeberg & Partner | 24 | beides ✓ |
| 30 | RWT | 12 | nur Titel/URL |

Die übrigen 21 Unternehmen haben `selectors=None` (siehe Kommentare in
`companies_config.py`). Sie werden im Lauf übersprungen, bis die Selektoren
hinterlegt sind.

### Typische Gründe, warum ein Unternehmen noch ohne Selektoren ist
- **JS-gerendert** (WTS, BDO, dhpg): die Übersichtsseite lädt die Artikelkarten
  clientseitig nach. `requests` sieht nur ein Skeleton-HTML. Lösung: später eine
  Playwright-Variante einbauen oder eine alternative server-gerenderte URL finden.
- **PDF-Newsletter-Archiv** (Dornbach): keine Artikel, sondern monatliche PDF-Editionen.
  Strukturell anders — bräuchte eigenes Mapping.
- **Falsche URL** (Clifford Chance, Linklaters): die Quelltabelle zeigt auf eine
  Praxisgruppen-/Karriereseite. URL in `companies_config.py` auf eine echte News-/
  Insights-Seite ändern.
- **Noch nicht inspiziert** (alle anderen): nach gleichem Muster wie die Piloten ausbauen.

## Output
**`LATEST_REPORT.md`** — Beispiel:

```
# Neue Steuer-News — 25.05.2026

**4 neue Beiträge von 2 Unternehmen**

## KPMG (3)

- **Neuntes Gesetz zur Änderung des StBerG…**
  https://kpmg.com/de/de/themen/2026/01/reg-e-gewst-hebesatz.html
  > BR-Drs. 223/26

## EY (1)

- **2026-04-23 — Wichtige Steuertermine**
  https://www.ey.com/de_de/technical/steuernachrichten/wichtige-steuertermine13
  > Zum 31.05.2026 ist u. a. der Fristablauf …

---
*Abruf: 25.05.2026 07:02 UTC*
```

## Manuell ausführen (lokal)
```bash
pip install -r requirements.txt

# Alle aktiven Unternehmen:
python main.py

# Nur ausgewählte (zum Selektor-Testen):
python main.py --only ey,kpmg,deloitte

# State zurücksetzen (führt zu neuem Seed-Lauf für alle):
python main.py --reset-state
```

## In GitHub Actions auslösen
**Actions → "Monitor Tax News" → Run workflow → Branch `main` → Run workflow.**

Keine Secrets nötig.

## Neue Selektoren für ein Unternehmen hinterlegen

1. Lokal die Seite holen und HTML cachen:
   ```python
   from tools.fetch_page import fetch
   open('tmp/html/<key>.html','w').write(fetch('<url>').html)
   ```
2. Im Browser DevTools auf der Seite öffnen, eine Artikelkarte inspizieren.
   Notieren:
   - **Container** der einzelnen Karte (eindeutige Klasse, z. B. `div.news-item`)
   - **Titel** relativ zur Karte (z. B. `h3.title`)
   - **URL**, wenn das Titel-Element nicht direkt der Link ist (z. B. `a.read-more`)
   - **Datum** (falls vorhanden, z. B. `time[datetime]` oder `span.date`)
   - **Zusammenfassung** (falls vorhanden, z. B. `p.excerpt`)
3. In `companies_config.py` für das Unternehmen einen `SiteSelectors`-Eintrag
   anlegen.
4. Lokal testen:
   ```bash
   python main.py --only <key>
   ```
   Prüfen, dass im Log echte Artikeltitel/URLs/Daten erscheinen.

## Selektoren reparieren, wenn ein Unternehmen plötzlich 0 Treffer liefert

Wenn ein bisher funktionierender Lauf für ein Unternehmen 0 Artikel meldet:
1. Die Seite hat sich vermutlich umgestaltet.
2. Lokales HTML neu holen, DevTools öffnen, neue Klassen identifizieren.
3. Selektoren in `companies_config.py` aktualisieren.
4. `python main.py --only <key>` zum Verifizieren.

## Hinweis zur Datumsnormalisierung
`tools/scrape_articles.py` versucht Datumsangaben in das ISO-Format `YYYY-MM-DD`
zu normalisieren. Unterstützt:
- `YYYY-MM-DD` (auch mit Uhrzeit-Suffix)
- `12.05.2026`
- `5 März 2026`, `23 Apr. 2026` (lange & abgekürzte deutsche Monatsnamen)

Wenn eine Karte sein Datum in einer ungewöhnlichen Form ausgibt, kann pro
Unternehmen in `SiteSelectors.date_formats` ein zusätzliches Format ergänzt
werden.

## Zeitplan
GitHub Actions führt den Workflow montags 07:00 UTC aus (08:00 CET / 09:00 CEST).
