# Finanzgerichte – Überwachte Quellen

Der Agent durchsucht jede Woche automatisch (montags 08:00 Uhr) die unten aufgeführten Quellen nach neuen Entscheidungen der deutschen Finanzgerichte. Berichtszeitraum: letzte 4 Wochen. Im Bericht erscheinen nur Entscheidungen, die seit dem letzten Bericht neu hinzugekommen sind.

---

## Primärquelle: dejure.org

**dejure.org** ist eine kostenlose deutsche Rechtsdatenbank und dient als Hauptquelle für alle Finanzgerichte. Die URLs sind bereits nach Gericht gefiltert – es werden ausschließlich Finanzgerichtsentscheidungen abgerufen.

| Gericht | dejure-URL | Status |
|---|---|---|
| FG Baden-Württemberg | [dejure](https://dejure.org/dienste/rechtsprechung?gericht=FG%20Baden-W%FCrttemberg) | ✅ aktiv |
| FG München | [dejure](https://dejure.org/dienste/rechtsprechung?gericht=FG%20M%FCnchen) | ✅ aktiv |
| FG Nürnberg | [dejure](https://dejure.org/dienste/rechtsprechung?gericht=FG%20N%FCrnberg) | ✅ aktiv |
| FG Berlin-Brandenburg | [dejure](https://dejure.org/dienste/rechtsprechung?gericht=FG%20Berlin%2DBrandenburg) | ✅ aktiv |
| FG Brandenburg | [dejure](https://dejure.org/dienste/rechtsprechung?gericht=FG%20Brandenburg) | ✅ aktiv |
| FG Bremen | [dejure](https://dejure.org/dienste/rechtsprechung?gericht=FG%20Bremen) | ✅ aktiv |
| FG Düsseldorf | [dejure](https://dejure.org/dienste/rechtsprechung?gericht=FG%20D%FCsseldorf) | ✅ aktiv |
| FG Hamburg | [dejure](https://dejure.org/dienste/rechtsprechung?gericht=FG%20Hamburg) | ✅ aktiv |
| FG Hessen | [dejure](https://dejure.org/dienste/rechtsprechung?gericht=FG%20Hessen) | ✅ aktiv |
| FG Köln | [dejure](https://dejure.org/dienste/rechtsprechung?gericht=FG%20K%F6ln) | ✅ aktiv |
| FG Mecklenburg-Vorpommern | [dejure](https://dejure.org/dienste/rechtsprechung?gericht=FG%20Mecklenburg%2DVorpommern) | ✅ aktiv |
| FG Münster | [dejure](https://dejure.org/dienste/rechtsprechung?gericht=FG%20M%FCnster) | ✅ aktiv |
| FG Niedersachsen | [dejure](https://dejure.org/dienste/rechtsprechung?gericht=FG%20Niedersachsen) | ✅ aktiv |
| FG Rheinland-Pfalz | [dejure](https://dejure.org/dienste/rechtsprechung?gericht=FG%20Rheinland%2DPfalz) | ✅ aktiv |
| FG Saarland | [dejure](https://dejure.org/dienste/rechtsprechung?gericht=FG%20Saarland) | ✅ aktiv |
| FG Sachsen | [dejure](https://dejure.org/dienste/rechtsprechung?gericht=FG%20Sachsen) | ✅ aktiv |
| FG Sachsen-Anhalt | [dejure](https://dejure.org/dienste/rechtsprechung?gericht=FG%20Sachsen%2DAnhalt) | ✅ aktiv |
| FG Schleswig-Holstein | [dejure](https://dejure.org/dienste/rechtsprechung?gericht=FG%20Schleswig%2DHolstein) | ✅ aktiv |
| FG Thüringen | [dejure](https://dejure.org/dienste/rechtsprechung?gericht=FG%20Th%FCringen) | ✅ aktiv |

---

## Sekundärquelle: Voris (Niedersachsen)

FG Niedersachsen wird zusätzlich über das Wolters Kluwer Voris-Portal abgerufen, das direkt nach Finanzgerichtsentscheidungen filtert.

| Gericht | URL | Status |
|---|---|---|
| FG Niedersachsen | [Voris – Rechtsprechung Finanzgerichte](https://voris.wolterskluwer-online.de/search?query=&sort_order=date_desc&publicationtype=publicationform-ats-filter!ATS_Rechtsprechung_Finanzgerichte_FG) | ✅ aktiv |

---

## Weitere Quellen (Referenz / manuell prüfbar)

Die folgenden Quellen sind bekannt, werden aber aus den unten angegebenen Gründen **nicht automatisch** abgerufen.

### Landesrechtsdatenbanken (juris Bürgerservice – React-SPA)

Diese Portale enthalten Entscheidungen aller Gerichtstypen. Eine automatische Filterung auf „Finanzgericht" ist technisch per Playwright möglich, aber auf jedem Portal unterschiedlich implementiert. Da dejure.org dieselben Entscheidungen bereits gefiltert bereitstellt, wird auf eine separate Implementierung verzichtet.

| Gericht | URL | Hinweis |
|---|---|---|
| FG Baden-Württemberg | [landesrecht-bw.de](https://www.landesrecht-bw.de/bsbw?query=AUTOR:%22FG%22) | FG-Filter über Query-Parameter möglich |
| FG Berlin-Brandenburg | [gesetze.berlin.de](https://gesetze.berlin.de/bsbe/search) | Filter muss manuell gesetzt werden |
| FG Hamburg | [landesrecht-hamburg.de](https://www.landesrecht-hamburg.de/bsha/search) | Filter muss manuell gesetzt werden |
| FG Hessen | [hessenrecht.hessen.de](https://www.rv.hessenrecht.hessen.de/bshe/search) | Filter muss manuell gesetzt werden |
| FG Mecklenburg-Vorpommern | [landesrecht-mv.de](https://www.landesrecht-mv.de/bsmv/search) | Filter muss manuell gesetzt werden |
| FG Rheinland-Pfalz | [landesrecht.rlp.de](https://www.landesrecht.rlp.de/bsrp/search) | Filter muss manuell gesetzt werden |
| FG Sachsen-Anhalt | [landesrecht.sachsen-anhalt.de](https://www.landesrecht.sachsen-anhalt.de/bsst/search) | Filter muss manuell gesetzt werden |
| FG Schleswig-Holstein | [gesetze-rechtsprechung.sh.juris.de](https://www.gesetze-rechtsprechung.sh.juris.de/bssh/search) | Filter muss manuell gesetzt werden |
| FG Thüringen | [landesrecht.thueringen.de](https://www.landesrecht.thueringen.de/bsth/search) | Filter muss manuell gesetzt werden |

### Saarland – Offizielle Pressemitteilungen

| Gericht | URL | Hinweis |
|---|---|---|
| FG Saarland | [saarland.de – Entscheidungen](https://www.saarland.de/fgds/DE/pressemitteilungen/pm_Entscheidungen) | ❌ Durch Cloudflare WAF geschützt – automatischer Zugriff nicht möglich |

### Bayern – Gesetze Bayern Portal

| Gericht | URL | Hinweis |
|---|---|---|
| FG München / Nürnberg | [gesetze-bayern.de – Finanzgerichtsbarkeit](https://www.gesetze-bayern.de/Search/Filter/LEVEL1RSPRTREENODE/Finanzgerichtsbarkeit) | Gefilterte Seite, aber React-SPA ohne direkten Seiteninhalt beim Laden |

### Sachsen – Justizportal

| Gericht | URL | Hinweis |
|---|---|---|
| FG Sachsen | [justiz.sachsen.de](https://www.justiz.sachsen.de/esamosplus/pages/suchen.aspx) | ASP.NET-Formular, kein FG als Gerichtstyp wählbar |

### NRW – Justizportal

| Gericht | URL | Hinweis |
|---|---|---|
| FG Köln / Düsseldorf / Münster | [nrwesuche.justiz.nrw.de](https://nrwesuche.justiz.nrw.de/index.php#solrNrwe) | JavaScript-Hash-Router, Playwright nötig |

### Beck Online (kostenpflichtig)

Die folgenden Beck Online-URLs erfordern ein Abonnement und können **nicht automatisch** abgerufen werden.

| Gericht | Hinweis |
|---|---|
| FG Rheinland-Pfalz | Paywall – beck-online.beck.de |
| FG Schleswig-Holstein | Paywall – beck-online.beck.de |
| FG Hessen | Paywall – beck-online.beck.de |
| FG Mecklenburg-Vorpommern | Paywall – beck-online.beck.de |

---

## Zusammenfassung: Abdeckung

| Gesamt Gerichte | Automatisch überwacht | Nicht zugänglich |
|---|---|---|
| 19 | 19 (alle über dejure.org) | 0 |

> **Hinweis:** FG Bremen, FG Saarland, FG Sachsen und FG Thüringen waren zuvor nicht überwacht. Mit dejure.org sind jetzt alle deutschen Finanzgerichte abgedeckt.
