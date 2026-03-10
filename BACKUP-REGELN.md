# Backup- & Sicherheitsregeln — go.myimpactflow.ch

## Goldene Regeln

> **JEDE Seite ist kritisch.** Wenn eine URL ausfällt, brechen RefLinks, Partner-Systeme und Funnels.
>
> **VOR jeder Änderung:** `python3 check-live-urls.py --pre`
> **NACH dem Deploy:** `python3 check-live-urls.py --post`
> **Regelmässig:** `python3 backup-manager.py backup`

---

## Architektur

```
go.myimpactflow.ch/                      ← MyImpactFlow.github.io (User Pages)
go.myimpactflow.ch/herz-analyse.html     ← MyImpactFlow.github.io
go.myimpactflow.ch/danke.html            ← MyImpactFlow.github.io
go.myimpactflow.ch/impressum.html        ← MyImpactFlow.github.io
go.myimpactflow.ch/datenschutz.html      ← MyImpactFlow.github.io
go.myimpactflow.ch/revlink.html          ← MyImpactFlow.github.io
go.myimpactflow.ch/impact-flow-slides/   ← impact-flow-slides (Project Pages)
```

### Repos

| Repo | Zweck | Domain-Pfad |
|------|-------|-------------|
| `MyImpactFlow.github.io` | **Landing Pages + Domain-Hub** | `/` (Root) |
| `impact-flow-slides` | Slides Dashboard + Präsentationen | `/impact-flow-slides/` |
| `whatsapp-funnel` | ⚠️ ARCHIV — nicht mehr aktiv für Domain | — |

### Wichtig

- **`MyImpactFlow.github.io`** ist die einzige Quelle für Root-Seiten unter `go.myimpactflow.ch`
- **`whatsapp-funnel`** ist nur noch als Archiv/Backup vorhanden — Änderungen an Landing Pages gehen NUR in `MyImpactFlow.github.io`
- Projekt-Repos (wie `impact-flow-slides`) werden automatisch als Unterordner bereitgestellt

---

## Sicherheitsnetz: 4 Werkzeuge

### 1. `live-urls.json` — URL-Registry (ALLE kritisch!)

Zentrale Liste ALLER Live-URLs. JEDE URL ist kritisch markiert.

**Pflicht:** Bei jeder neuen Seite → URL hier eintragen!

### 2. `check-live-urls.py` — URL-Checker

```bash
python3 check-live-urls.py --pre     # VOR dem Deployment (Snapshot)
python3 check-live-urls.py --post    # NACH dem Deployment (Vergleich)
python3 check-live-urls.py           # Einfacher Check
python3 check-live-urls.py --watch   # Monitoring alle 30s
```

### 3. `backup-manager.py` — Vollständiges Backup & Restore

```bash
python3 backup-manager.py backup     # Backup aller Live-Dateien (HTML, CNAME, docs/)
python3 backup-manager.py list       # Alle Backups anzeigen
python3 backup-manager.py verify     # Aktuellen Stand gegen Backup prüfen
python3 backup-manager.py restore    # Letztes Backup 1:1 wiederherstellen
```

**Was wird gesichert:**
- Alle HTML-Dateien (Landing Pages, Danke-Seiten, RefLink-Generatoren)
- CNAME-Datei (Domain-Zuordnung)
- docs/-Ordner (PDFs, Dokumentation)
- SHA-256 Prüfsummen jeder einzelnen Datei

**Was passiert beim Restore:**
1. Sicherheitskopie des aktuellen (kaputten) Stands
2. Alle Dateien aus dem Backup zurückkopieren
3. Jede Datei gegen SHA-256 Hash verifizieren
4. Anleitung zum Push anzeigen

### 4. `backups/` — Lokale Backup-Kopien

Vollständige Kopie aller Live-Dateien. Bleibt IMMER lokal auf dem Mac.
Wird NIE gelöscht. Wird NIE in Git gepusht.

---

## Verbotene Aktionen ⛔

1. **NIEMALS die CNAME-Datei löschen oder ändern** ohne vorherigen Pre-Flight-Check
2. **NIEMALS Dateien in `MyImpactFlow.github.io` überschreiben** ohne Backup
3. **NIEMALS GitHub Pages deaktivieren** auf einem Repo, das Live-Seiten hostet
4. **NIEMALS einen Custom-Domain auf ein anderes Repo verschieben** ohne alle Seiten vorher zu migrieren
5. **NIEMALS `backups/`-Ordner löschen** — das ist die letzte Rettungsleine

---

## Deployment-Checkliste

### Neue Landing Page hinzufügen

1. ✅ `python3 backup-manager.py backup` — Aktuellen Stand sichern
2. ✅ `python3 check-live-urls.py --pre` — Alle URLs prüfen
3. ✅ Neue HTML-Datei erstellen
4. ✅ URL in `live-urls.json` eintragen
5. ✅ `git add`, `git commit`, `git push`
6. ✅ 30s warten (GitHub Pages Build)
7. ✅ `python3 check-live-urls.py --post` — Alles noch da?

### Bestehende Seite ändern

1. ✅ `python3 backup-manager.py backup` — PFLICHT vor jeder Änderung
2. ✅ `python3 check-live-urls.py --pre`
3. ✅ Änderung durchführen
4. ✅ `git add`, `git commit`, `git push`
5. ✅ `python3 check-live-urls.py --post`

### Domain-Änderungen (GEFÄHRLICH!)

1. ✅ `python3 backup-manager.py backup` — PFLICHT!
2. ✅ `python3 check-live-urls.py --pre` — PFLICHT!
3. ✅ `python3 check-live-urls.py --watch` in einem separaten Terminal
4. ✅ Änderung durchführen
5. ✅ Sofort `python3 check-live-urls.py --post`
6. ✅ Falls Fehler: Sofort `python3 backup-manager.py restore` + Push

---

## Notfall-Recovery (Seiten offline!)

```bash
# 1. Was ist kaputt?
python3 check-live-urls.py

# 2. Welche Dateien fehlen/geändert?
python3 backup-manager.py verify

# 3. ALLES aus Backup wiederherstellen
python3 backup-manager.py restore

# 4. Wiederhergestellte Dateien pushen
git add -A
git commit -m "Notfall-Restore aus Backup"
git push origin main

# 5. Prüfen ob alles wieder da ist
python3 check-live-urls.py --post
```

Falls auch Git kaputt ist:
```bash
# CNAME prüfen
cat CNAME  # Muss "go.myimpactflow.ch" enthalten

# GitHub Pages Status
gh api repos/MyImpactFlow/MyImpactFlow.github.io/pages --jq '.status'

# Letzten guten Commit finden
git log --oneline -10
git revert HEAD
git push
```
