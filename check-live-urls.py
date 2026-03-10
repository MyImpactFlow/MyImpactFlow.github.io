#!/usr/bin/env python3
"""
ImpactFlow Live-URL-Checker — Sicherheitsnetz für go.myimpactflow.ch

Prüft alle registrierten URLs auf Erreichbarkeit.
Verhindert, dass Deployments Live-Seiten zerstören.

Aufruf:
  python3 check-live-urls.py              # Alle URLs prüfen
  python3 check-live-urls.py --pre        # Pre-Flight: Snapshot speichern
  python3 check-live-urls.py --post       # Post-Deploy: Gegen Snapshot vergleichen
  python3 check-live-urls.py --watch      # Alle 30s prüfen (für Deployment-Monitoring)

Rückgabecodes:
  0 = Alles OK
  1 = Mindestens eine kritische URL ist down
  2 = Nicht-kritische URLs down (Warnung)
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime

# Pfade
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REGISTRY_PATH = os.path.join(SCRIPT_DIR, 'live-urls.json')
SNAPSHOT_DIR = os.path.join(SCRIPT_DIR, '.url-snapshots')


def load_registry():
    """Lädt die URL-Registry."""
    if not os.path.exists(REGISTRY_PATH):
        print(f'❌ Registry nicht gefunden: {REGISTRY_PATH}')
        sys.exit(1)

    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def check_url(url, timeout=15):
    """Prüft eine einzelne URL. Gibt (status_code, response_time_ms) zurück."""
    start = time.time()
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'ImpactFlow-URLChecker/1.0')
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            elapsed = int((time.time() - start) * 1000)
            return resp.status, elapsed
    except urllib.error.HTTPError as e:
        elapsed = int((time.time() - start) * 1000)
        return e.code, elapsed
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        return 0, elapsed


def check_all(seiten):
    """Prüft alle URLs und gibt Ergebnisse zurück."""
    ergebnisse = []
    for seite in seiten:
        url = seite['url']
        status, ms = check_url(url)
        ok = 200 <= status < 400
        ergebnisse.append({
            'url': url,
            'status': status,
            'ms': ms,
            'ok': ok,
            'kritisch': seite.get('kritisch', False),
            'beschreibung': seite.get('beschreibung', ''),
            'repo': seite.get('repo', ''),
        })
    return ergebnisse


def print_results(ergebnisse, titel='URL-Check'):
    """Zeigt die Ergebnisse formatiert an."""
    print(f'\n{"=" * 60}')
    print(f'  {titel}')
    print(f'  {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}')
    print(f'{"=" * 60}\n')

    ok_count = sum(1 for e in ergebnisse if e['ok'])
    fail_count = len(ergebnisse) - ok_count

    for e in ergebnisse:
        icon = '✅' if e['ok'] else '❌'
        kritisch = ' ⚠️  KRITISCH!' if not e['ok'] and e['kritisch'] else ''
        status_text = str(e['status']) if e['status'] > 0 else 'TIMEOUT'
        print(f'  {icon} [{status_text}] {e["ms"]:>4}ms  {e["url"]}{kritisch}')

    print(f'\n{"─" * 60}')
    print(f'  Ergebnis: {ok_count}/{len(ergebnisse)} URLs erreichbar', end='')
    if fail_count > 0:
        kritisch_down = sum(1 for e in ergebnisse if not e['ok'] and e['kritisch'])
        print(f'  |  ❌ {fail_count} fehlgeschlagen ({kritisch_down} kritisch)')
    else:
        print(f'  |  ✅ Alles OK')
    print(f'{"─" * 60}\n')

    return fail_count == 0


def save_snapshot(ergebnisse):
    """Speichert einen Snapshot der aktuellen URL-Zustände."""
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)

    snapshot = {
        'timestamp': datetime.now().isoformat(),
        'ergebnisse': ergebnisse
    }

    # Aktueller Snapshot
    snapshot_path = os.path.join(SNAPSHOT_DIR, 'latest.json')
    with open(snapshot_path, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    # Historischer Snapshot
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    history_path = os.path.join(SNAPSHOT_DIR, f'snapshot_{ts}.json')
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    print(f'  📸 Snapshot gespeichert: {snapshot_path}')
    return snapshot_path


def compare_with_snapshot(ergebnisse):
    """Vergleicht aktuelle Ergebnisse mit dem letzten Snapshot."""
    snapshot_path = os.path.join(SNAPSHOT_DIR, 'latest.json')

    if not os.path.exists(snapshot_path):
        print('  ⚠️  Kein Snapshot vorhanden. Führe zuerst --pre aus.')
        return True  # Kein Vergleich möglich

    with open(snapshot_path, 'r', encoding='utf-8') as f:
        snapshot = json.load(f)

    print(f'\n  📊 Vergleich mit Snapshot vom {snapshot["timestamp"][:19]}')
    print(f'  {"─" * 50}')

    # Erstelle Lookup für Snapshot
    snap_lookup = {e['url']: e for e in snapshot['ergebnisse']}

    verschlechtert = []
    verbessert = []

    for e in ergebnisse:
        url = e['url']
        if url in snap_lookup:
            war_ok = snap_lookup[url]['ok']
            ist_ok = e['ok']

            if war_ok and not ist_ok:
                verschlechtert.append(e)
                print(f'  🔴 REGRESSION: {url}')
                print(f'       Vorher: {snap_lookup[url]["status"]} → Jetzt: {e["status"]}')
            elif not war_ok and ist_ok:
                verbessert.append(e)
                print(f'  🟢 BEHOBEN:    {url}')
        else:
            if e['ok']:
                print(f'  🆕 NEU (OK):   {url}')
            else:
                print(f'  🆕 NEU (FAIL): {url}')

    if not verschlechtert and not verbessert:
        print(f'  ✅ Keine Änderungen — alle Seiten gleich wie vorher.')

    print()

    if verschlechtert:
        kritisch = [v for v in verschlechtert if v['kritisch']]
        if kritisch:
            print(f'  🚨 {len(kritisch)} KRITISCHE SEITE(N) DURCH DEPLOYMENT KAPUTT!')
            print(f'     SOFORT RÜCKGÄNGIG MACHEN!')
            return False
        else:
            print(f'  ⚠️  {len(verschlechtert)} nicht-kritische Seite(n) betroffen.')
            return True

    return True


def watch_mode(seiten, interval=30):
    """Prüft alle URLs in einer Endlosschleife."""
    print(f'  👁️  Watch-Modus — Prüfe alle {interval}s (Ctrl+C zum Beenden)\n')
    try:
        while True:
            ergebnisse = check_all(seiten)
            all_ok = print_results(ergebnisse, 'Watch-Modus')
            if not all_ok:
                print('  🔔 ALARM: Seiten nicht erreichbar!\n')
            time.sleep(interval)
    except KeyboardInterrupt:
        print('\n  ⏹️  Watch-Modus beendet.')


def main():
    data = load_registry()
    seiten = data.get('seiten', [])

    if not seiten:
        print('Keine URLs in der Registry.')
        return

    # Modus bestimmen
    mode = 'check'
    if '--pre' in sys.argv:
        mode = 'pre'
    elif '--post' in sys.argv:
        mode = 'post'
    elif '--watch' in sys.argv:
        mode = 'watch'

    if mode == 'watch':
        watch_mode(seiten)
        return

    # URLs prüfen
    ergebnisse = check_all(seiten)

    if mode == 'pre':
        all_ok = print_results(ergebnisse, '🛫 Pre-Flight-Check')
        if all_ok:
            save_snapshot(ergebnisse)
            print('  ✅ Alle URLs erreichbar. Deployment kann starten.\n')
        else:
            save_snapshot(ergebnisse)
            kritisch_down = [e for e in ergebnisse if not e['ok'] and e['kritisch']]
            if kritisch_down:
                print('  🚨 STOPP! Kritische Seiten sind bereits DOWN.')
                print('     Kläre das zuerst, bevor du Änderungen machst.\n')
                sys.exit(1)
            else:
                print('  ⚠️  Nicht-kritische Seiten sind down. Deployment mit Vorsicht.\n')
                sys.exit(2)

    elif mode == 'post':
        all_ok = print_results(ergebnisse, '🛬 Post-Deploy-Check')
        vergleich_ok = compare_with_snapshot(ergebnisse)
        if all_ok and vergleich_ok:
            print('  ✅ Deployment erfolgreich — keine Regressionen.\n')
            save_snapshot(ergebnisse)  # Neuen Snapshot speichern
        elif not vergleich_ok:
            print('  🚨 DEPLOYMENT HAT SEITEN ZERSTÖRT!')
            print('  ➡️  git revert oder manuell reparieren!\n')
            sys.exit(1)
        else:
            print('  ⚠️  Einige Seiten nicht erreichbar (war aber schon vorher so).\n')
            sys.exit(2)

    else:
        all_ok = print_results(ergebnisse, '🔍 URL-Check')
        if not all_ok:
            kritisch_down = [e for e in ergebnisse if not e['ok'] and e['kritisch']]
            sys.exit(1 if kritisch_down else 2)


if __name__ == '__main__':
    main()
