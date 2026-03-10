# Backup- & Sicherheitsregeln — go.myimpactflow.ch

## Goldene Regel

> **Bevor du etwas änderst, das Live-Seiten betreffen könnte: `python3 check-live-urls.py --pre`**
> **Nachdem du deployed hast: `python3 check-live-urls.py --post`**

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

## Sicherheitsnetz: 3 Dateien

### 1. `live-urls.json` — URL-Registry

Zentrale Liste ALLER Live-URLs. Wird vom Check-Script gelesen.

**Pflicht:** Bei jeder neuen Seite → URL hier eintragen!

### 2. `check-live-urls.py` — URL-Checker

```bash
# VOR dem Deployment
python3 check-live-urls.py --pre

# NACH dem Deployment
python3 check-live-urls.py --post

# Einfacher Check
python3 check-live-urls.py

# Monitoring (alle 30s)
python3 check-live-urls.py --watch
```

### 3. `.url-snapshots/` — Automatische Snapshots

Pre-Flight speichert den aktuellen Zustand. Post-Deploy vergleicht dagegen und schlägt Alarm, wenn Seiten neu kaputt sind.

---

## Verbotene Aktionen ⛔

1. **NIEMALS die CNAME-Datei löschen oder ändern** ohne vorherigen Pre-Flight-Check
2. **NIEMALS Dateien in `MyImpactFlow.github.io` überschreiben** ohne zu prüfen, welche Live-Seiten betroffen sind
3. **NIEMALS GitHub Pages deaktivieren** auf einem Repo, das Live-Seiten hostet
4. **NIEMALS einen Custom-Domain auf ein anderes Repo verschieben** ohne alle Seiten vorher zu migrieren

---

## Deployment-Checkliste

### Neue Landing Page hinzufügen

1. ✅ `python3 check-live-urls.py --pre`
2. ✅ Neue HTML-Datei in `MyImpactFlow.github.io` erstellen
3. ✅ URL in `live-urls.json` eintragen
4. ✅ `git add`, `git commit`, `git push`
5. ✅ 30s warten (GitHub Pages Build)
6. ✅ `python3 check-live-urls.py --post`

### Bestehendes Projekt als Subpath hinzufügen

1. ✅ `python3 check-live-urls.py --pre`
2. ✅ Neues Repo erstellen + GitHub Pages aktivieren (KEIN Custom Domain!)
3. ✅ Repo-URLs in `live-urls.json` eintragen
4. ✅ Push + warten
5. ✅ `python3 check-live-urls.py --post`

### Domain-Änderungen (GEFÄHRLICH!)

1. ✅ `python3 check-live-urls.py --pre` — PFLICHT!
2. ✅ Alle Seiten VOR der Änderung dokumentieren
3. ✅ `python3 check-live-urls.py --watch` in einem separaten Terminal starten
4. ✅ Änderung durchführen
5. ✅ Sofort `python3 check-live-urls.py --post`
6. ✅ Falls Fehler: Sofort `git revert` + Push

---

## Notfall-Recovery

Falls Seiten plötzlich offline sind:

```bash
# 1. Status prüfen
python3 check-live-urls.py

# 2. GitHub Pages Status prüfen
gh api repos/MyImpactFlow/MyImpactFlow.github.io/pages --jq '.status'

# 3. CNAME prüfen
cat CNAME  # Muss "go.myimpactflow.ch" enthalten

# 4. Letzten funktionierenden Commit finden
git log --oneline -10

# 5. Zurücksetzen
git revert HEAD
git push
```
