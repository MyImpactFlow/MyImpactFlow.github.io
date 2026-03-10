#!/usr/bin/env python3
"""
ImpactFlow Backup-Manager — Vollständiges Backup & Restore

Erstellt minutiöse Backups aller Live-Seiten und kann diese
1:1 wiederherstellen, damit RefLinks und alle Systeme funktionieren.

Aufruf:
  python3 backup-manager.py backup             # Vollständiges Backup erstellen
  python3 backup-manager.py list               # Alle Backups anzeigen
  python3 backup-manager.py verify             # Aktuellen Stand gegen Backup prüfen
  python3 backup-manager.py restore             # Letztes Backup wiederherstellen
  python3 backup-manager.py restore 20260310   # Bestimmtes Backup wiederherstellen

Backup-Inhalt:
  - Jede HTML-Datei vollständig kopiert
  - CNAME-Datei (Domain-Zuordnung)
  - docs/-Ordner komplett
  - SHA-256 Prüfsummen aller Dateien
  - Manifest mit Dateigrössen und Zeitstempeln
"""

import hashlib
import json
import os
import shutil
import sys
from datetime import datetime

# Pfade
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(SCRIPT_DIR, 'backups')

# Dateien und Ordner, die NICHT gesichert werden (sind Tool-Dateien, keine Live-Seiten)
EXCLUDE = {
    '.git', '.gitignore', '.DS_Store', '.url-snapshots', '.claude',
    'backups', 'check-live-urls.py', 'backup-manager.py',
    'live-urls.json', 'BACKUP-REGELN.md', 'PROJEKT.md',
    '__pycache__', '.venv', 'venv'
}


def sha256(filepath):
    """Berechnet SHA-256 Hash einer Datei."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def get_live_files():
    """Sammelt alle Live-Dateien (HTML, CNAME, docs/, etc.)."""
    live_files = []

    for root, dirs, files in os.walk(SCRIPT_DIR):
        # Ausgeschlossene Ordner überspringen
        dirs[:] = [d for d in dirs if d not in EXCLUDE]

        for fname in files:
            if fname in EXCLUDE:
                continue
            if fname.startswith('.') and fname != '.nojekyll':
                continue

            filepath = os.path.join(root, fname)
            relpath = os.path.relpath(filepath, SCRIPT_DIR)

            # Backup-Ordner selbst überspringen
            if relpath.startswith('backups'):
                continue

            live_files.append({
                'relpath': relpath,
                'fullpath': filepath,
                'size': os.path.getsize(filepath),
                'mtime': os.path.getmtime(filepath),
            })

    return sorted(live_files, key=lambda f: f['relpath'])


def create_backup():
    """Erstellt ein vollständiges Backup aller Live-Dateien."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(BACKUP_DIR, f'backup_{timestamp}')
    os.makedirs(backup_path, exist_ok=True)

    live_files = get_live_files()
    manifest = {
        'timestamp': datetime.now().isoformat(),
        'datum': datetime.now().strftime('%d.%m.%Y %H:%M'),
        'dateien': [],
        'gesamt_dateien': 0,
        'gesamt_bytes': 0,
    }

    print(f'\n  📦 Backup wird erstellt: {backup_path}\n')

    for f in live_files:
        relpath = f['relpath']
        src = f['fullpath']
        dst = os.path.join(backup_path, relpath)

        # Zielordner erstellen
        os.makedirs(os.path.dirname(dst), exist_ok=True)

        # Datei kopieren
        shutil.copy2(src, dst)

        # Hash berechnen
        file_hash = sha256(src)

        manifest['dateien'].append({
            'pfad': relpath,
            'groesse': f['size'],
            'sha256': file_hash,
            'mtime': datetime.fromtimestamp(f['mtime']).isoformat(),
        })

        size_kb = f['size'] / 1024
        print(f'  ✅ {relpath:45s}  {size_kb:>7.1f} KB  {file_hash[:12]}...')

    manifest['gesamt_dateien'] = len(manifest['dateien'])
    manifest['gesamt_bytes'] = sum(d['groesse'] for d in manifest['dateien'])

    # Manifest speichern
    manifest_path = os.path.join(backup_path, '_manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as mf:
        json.dump(manifest, mf, ensure_ascii=False, indent=2)

    # "latest" Symlink aktualisieren
    latest_link = os.path.join(BACKUP_DIR, 'latest')
    if os.path.exists(latest_link) or os.path.islink(latest_link):
        os.remove(latest_link)
    os.symlink(backup_path, latest_link)

    total_kb = manifest['gesamt_bytes'] / 1024
    print(f'\n  {"─" * 60}')
    print(f'  📦 Backup komplett: {manifest["gesamt_dateien"]} Dateien, {total_kb:.1f} KB')
    print(f'  📂 Gespeichert in:  {backup_path}')
    print(f'  🔗 Symlink:         {latest_link}')
    print(f'  {"─" * 60}\n')

    return backup_path


def list_backups():
    """Zeigt alle vorhandenen Backups an."""
    if not os.path.exists(BACKUP_DIR):
        print('\n  Keine Backups vorhanden.\n')
        return

    backups = []
    for entry in sorted(os.listdir(BACKUP_DIR)):
        if entry.startswith('backup_') and os.path.isdir(os.path.join(BACKUP_DIR, entry)):
            manifest_path = os.path.join(BACKUP_DIR, entry, '_manifest.json')
            if os.path.exists(manifest_path):
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                backups.append({
                    'ordner': entry,
                    'datum': manifest.get('datum', '?'),
                    'dateien': manifest.get('gesamt_dateien', 0),
                    'bytes': manifest.get('gesamt_bytes', 0),
                })

    if not backups:
        print('\n  Keine Backups vorhanden. Erstelle eins mit: python3 backup-manager.py backup\n')
        return

    # Ist eines davon "latest"?
    latest_target = None
    latest_link = os.path.join(BACKUP_DIR, 'latest')
    if os.path.islink(latest_link):
        latest_target = os.path.basename(os.path.realpath(latest_link))

    print(f'\n  {"=" * 65}')
    print(f'  📦 Vorhandene Backups')
    print(f'  {"=" * 65}\n')

    for b in backups:
        is_latest = ' ← AKTUELL' if b['ordner'] == latest_target else ''
        kb = b['bytes'] / 1024
        print(f'  📂 {b["ordner"]}  |  {b["datum"]}  |  {b["dateien"]} Dateien  |  {kb:.0f} KB{is_latest}')

    print(f'\n  Gesamt: {len(backups)} Backup(s)\n')


def verify_backup(backup_name=None):
    """Vergleicht den aktuellen Stand mit einem Backup."""
    if backup_name:
        backup_path = os.path.join(BACKUP_DIR, backup_name)
    else:
        backup_path = os.path.join(BACKUP_DIR, 'latest')
        if os.path.islink(backup_path):
            backup_path = os.path.realpath(backup_path)

    manifest_path = os.path.join(backup_path, '_manifest.json')
    if not os.path.exists(manifest_path):
        print(f'\n  ❌ Kein Backup gefunden: {backup_path}\n')
        return False

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    print(f'\n  {"=" * 60}')
    print(f'  🔍 Verifikation gegen Backup vom {manifest["datum"]}')
    print(f'  {"=" * 60}\n')

    aenderungen = []
    fehlend = []
    intakt = 0

    for datei_info in manifest['dateien']:
        pfad = datei_info['pfad']
        erwarteter_hash = datei_info['sha256']
        vollpfad = os.path.join(SCRIPT_DIR, pfad)

        if not os.path.exists(vollpfad):
            fehlend.append(pfad)
            print(f'  ❌ FEHLT:     {pfad}')
        else:
            aktueller_hash = sha256(vollpfad)
            if aktueller_hash != erwarteter_hash:
                aenderungen.append(pfad)
                print(f'  ⚠️  GEÄNDERT:  {pfad}')
            else:
                intakt += 1

    # Neue Dateien (im Repo, aber nicht im Backup)
    aktuelle_dateien = {f['relpath'] for f in get_live_files()}
    backup_dateien = {d['pfad'] for d in manifest['dateien']}
    neue = aktuelle_dateien - backup_dateien

    if neue:
        print()
        for n in sorted(neue):
            print(f'  🆕 NEU:       {n}')

    print(f'\n  {"─" * 60}')
    print(f'  ✅ Intakt:    {intakt}')
    if aenderungen:
        print(f'  ⚠️  Geändert:  {len(aenderungen)}')
    if fehlend:
        print(f'  ❌ Fehlend:   {len(fehlend)}')
    if neue:
        print(f'  🆕 Neu:       {len(neue)}')
    print(f'  {"─" * 60}')

    if fehlend or aenderungen:
        print(f'\n  💡 Zum Wiederherstellen: python3 backup-manager.py restore\n')
        return False
    else:
        print(f'\n  ✅ Alles identisch mit dem Backup — keine Abweichungen.\n')
        return True


def restore_backup(backup_name=None):
    """Stellt alle Dateien aus einem Backup wieder her."""
    if backup_name:
        # Suche nach passendem Backup (Teilname reicht)
        matches = []
        if os.path.exists(BACKUP_DIR):
            for entry in os.listdir(BACKUP_DIR):
                if backup_name in entry and os.path.isdir(os.path.join(BACKUP_DIR, entry)):
                    matches.append(entry)
        if not matches:
            print(f'\n  ❌ Kein Backup gefunden mit "{backup_name}"')
            print(f'  💡 Verfügbare Backups anzeigen: python3 backup-manager.py list\n')
            return False
        if len(matches) > 1:
            print(f'\n  ⚠️  Mehrere Backups gefunden:')
            for m in matches:
                print(f'     {m}')
            print(f'\n  Bitte genauer angeben.\n')
            return False
        backup_path = os.path.join(BACKUP_DIR, matches[0])
    else:
        backup_path = os.path.join(BACKUP_DIR, 'latest')
        if os.path.islink(backup_path):
            backup_path = os.path.realpath(backup_path)

    manifest_path = os.path.join(backup_path, '_manifest.json')
    if not os.path.exists(manifest_path):
        print(f'\n  ❌ Kein Backup gefunden: {backup_path}')
        print(f'  💡 Erstelle eins mit: python3 backup-manager.py backup\n')
        return False

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    print(f'\n  {"=" * 60}')
    print(f'  🔄 WIEDERHERSTELLUNG aus Backup vom {manifest["datum"]}')
    print(f'  {"=" * 60}\n')
    print(f'  ⚠️  Dies überschreibt {manifest["gesamt_dateien"]} Dateien!')
    print(f'  Backup-Quelle: {backup_path}\n')

    # Sicherheits-Check: Erstelle vorher ein Zwischen-Backup
    zwischen_backup = os.path.join(BACKUP_DIR, f'pre_restore_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    os.makedirs(zwischen_backup, exist_ok=True)

    print(f'  📸 Sicherheitskopie des aktuellen Stands...')
    current_files = get_live_files()
    for cf in current_files:
        dst = os.path.join(zwischen_backup, cf['relpath'])
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(cf['fullpath'], dst)
    print(f'  ✅ Gesichert in: {zwischen_backup}\n')

    # Dateien wiederherstellen
    restored = 0
    errors = 0

    for datei_info in manifest['dateien']:
        pfad = datei_info['pfad']
        src = os.path.join(backup_path, pfad)
        dst = os.path.join(SCRIPT_DIR, pfad)

        if not os.path.exists(src):
            print(f'  ❌ FEHLT im Backup: {pfad}')
            errors += 1
            continue

        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

            # Hash verifizieren
            actual_hash = sha256(dst)
            expected_hash = datei_info['sha256']

            if actual_hash == expected_hash:
                print(f'  ✅ {pfad}')
                restored += 1
            else:
                print(f'  ⚠️  {pfad} — Hash stimmt nicht überein!')
                errors += 1
        except Exception as e:
            print(f'  ❌ {pfad} — Fehler: {e}')
            errors += 1

    print(f'\n  {"─" * 60}')
    print(f'  ✅ Wiederhergestellt: {restored}/{manifest["gesamt_dateien"]} Dateien')
    if errors:
        print(f'  ❌ Fehler:            {errors}')
    print(f'  {"─" * 60}')

    if errors == 0:
        print(f'\n  ✅ Wiederherstellung komplett!')
        print(f'  ➡️  Jetzt pushen:')
        print(f'     cd {SCRIPT_DIR}')
        print(f'     git add -A')
        print(f'     git commit -m "Restore aus Backup {manifest["datum"]}"')
        print(f'     git push origin main')
        print(f'\n  ➡️  Dann prüfen:')
        print(f'     python3 check-live-urls.py --post\n')
    else:
        print(f'\n  ⚠️  Es gab Fehler. Prüfe die Ausgabe oben.\n')

    return errors == 0


def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)

    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1].lower()

    if command == 'backup':
        create_backup()
    elif command == 'list':
        list_backups()
    elif command == 'verify':
        backup_name = sys.argv[2] if len(sys.argv) > 2 else None
        verify_backup(backup_name)
    elif command == 'restore':
        backup_name = sys.argv[2] if len(sys.argv) > 2 else None
        restore_backup(backup_name)
    else:
        print(f'\n  ❌ Unbekannter Befehl: {command}')
        print(f'  Verfügbar: backup, list, verify, restore\n')


if __name__ == '__main__':
    main()
