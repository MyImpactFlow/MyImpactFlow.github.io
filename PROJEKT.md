# WhatsApp Funnel Landing Page

## Projekt-Steckbrief

| Feld | Wert |
|------|------|
| **Projekt** | WhatsApp Funnel Landing Page |
| **Marke** | ImpactFlow |
| **Zielgruppe** | Frauen, die ein eigenes Business aufbauen wollen |
| **Hosting** | GitHub Pages |
| **Domain** | `go.myimpactflow.ch` (Custom Domain) |
| **Repository** | `https://github.com/MyImpactFlow/whatsapp-funnel.git` |
| **Branch** | `main` |
| **Stand** | März 2026 |

---

## Dateistruktur

```
whatsapp-funnel-landing/
├── index.html              # Haupt-Landing-Page (87 KB)
├── revlink.html            # Ref-Link Generator für Partner (29 KB)
├── impressum.html          # Impressum (9 KB)
├── datenschutz.html        # Datenschutzerklärung (11 KB)
├── 404.html                # Weiterleitung für RevLinks
├── CNAME                   # Custom Domain: go.myimpactflow.ch
├── PROJEKT.md              # Diese Dokumentation
├── .claude/                # Claude Code Konfiguration
└── versionen/
    ├── v1-original.html    # Erste Version der Landing Page
    └── v2-design-feinschliff.html  # Zweite Version mit Design-Verbesserungen
```

---

## Seiten im Detail

### index.html — Haupt-Landing-Page

Die zentrale Conversion-Seite. Führt Besucherinnen zum WhatsApp-Chat.

**Sektionen (von oben nach unten):**
1. **Navigation** — Logo + "Jetzt chatten" CTA-Button
2. **Hero** — Typewriter-Titel, Badge ("100% kostenlos"), Hero-Bild
3. **Social Proof Notification** — Floating-Banner oben ("Katrin hat einen Termin gebucht")
4. **Pain Section** — "Du willst mehr, aber irgendwas hält dich zurück" (4 Pain-Cards)
5. **Promise Section** — "Was wäre, wenn du nicht mehr alleine kämpfst?" (3 Promise-Cards)
6. **Steps Section** — "So einfach geht es" (3 Schritte: WhatsApp beitreten → Fragen beantworten → Klarheit bekommen)
7. **Quote Section** — Zitat mit Typewriter-Effekt
8. **Final CTA** — "Bereit für dein Business?" + WhatsApp-Button
9. **Footer** — Logo, Impressum, Datenschutz, Ref-Link Generator

**Interaktive Elemente:**
- **Visitor Counter Widget** — Draggbare Kachel mit Live-Besucherzähler (Schweiz, Deutschland, Österreich, etc.)
  - Magnetischer Snap am oberen/unteren Bildschirmrand (Mobile)
  - Magnet-Icon bei Snap
  - Close-Button (X)
  - Social Proof: "via Website, LinkedIn, TikTok, etc."
  - "X chatten gerade"
- **Social Proof Notification** — Floating-Banner mit zufälligen Buchungen (Minuten + Stunden)
- **Typewriter-Effekte** — Hero-Titel + Quote-Sektion
- **Scroll-Animationen:**
  - Pain-Cards: Conic-Gradient-Border füllt sich beim Scrollen
  - Promise-Cards: Gleicher Effekt
  - Steps: Erscheinen sequenziell beim Scrollen, verschwinden beim Hochscrollen

### revlink.html — Ref-Link Generator

Partner können ihren persönlichen Empfehlungslink generieren.

**Features:**
- Input-Feld für den persönlichen REF Chat-Link
- Link-Generierung mit Short-Code (z.B. `go.myimpactflow.ch/GSa7A7`)
- Plattform-Tracking: LinkedIn, Facebook, Instagram, Reddit, TikTok, E-Mail
  - Checkboxen für Plattform-Auswahl
  - Plattform-spezifische Links mit `?src=` Parameter
- PDF-Download mit QR-Code, Anleitung, Plattform-Links
- ZIP-Download (PDF + Anleitung)
- Fortlaufende Dokumentennummer

### 404.html — RevLink-Weiterleitung

Fängt Short-Links ab (z.B. `/GSa7A7`) und leitet weiter zu `/?wa=GSa7A7`.
Query-Parameter (`?src=linkedin`) werden durchgereicht.

### impressum.html / datenschutz.html

Rechtliche Seiten. Gleicher Stil wie die Landing Page.

**Kontaktdaten:**
- Impact Flow
- Sperletweg 36, 8052 Zürich, Schweiz
- E-Mail: go@impactflow.ch

---

## Technische Details

### CSS-Variablen

```css
--pink: #f29cb6
--dark: #2d2d2d
--white: #faf8f6
--pink-soft: #fce8ef
--mint-soft: #e8f5f0
```

### Wichtige CSS-Techniken

| Technik | Verwendung |
|---------|-----------|
| `conic-gradient` mit `--bp` Custom Property | Animierte Border-Füllung bei Pain/Promise Cards |
| `display: contents` auf `.hero-text` | Mobile Grid-Reorder (Badge → Bild → Titel) |
| `@media (max-width: 600px)` | Mobile-First Breakpoint |
| `position: fixed` + Drag-Handler | Visitor Counter Widget |

### Wichtige JS-Patterns

| Pattern | Verwendung |
|---------|-----------|
| `IntersectionObserver` | Typewriter-Sichtbarkeit |
| Scroll-Listener (`passive: true`) | Card-Border-Animation, Steps-Reveal |
| `localStorage` | Partner-Link (`if_partner`), Source (`if_source`), Widget-Position (`vc_pos`) |
| Touch + Mouse Events | Widget-Drag (Touch: `touchstart/move/end`, Mouse: `mousedown/move/up`) |

### RevLink-System

```
Partner-Link: https://myimpactflow.ch/GSa7A7
  → 404.html fängt ab
  → Weiterleitung: /?wa=GSa7A7&src=linkedin
  → index.html liest ?wa= und ?src=
  → localStorage: if_partner + if_source
  → WhatsApp-Link wird mit Partner-Code generiert
```

---

## Feature-Chronologie

### Phase 1 — Grundlagen
- Landing Page Grundstruktur (Hero, Pain, Promise, Steps, CTA)
- Visitor Counter Widget mit Drag-Funktion
- Mobile-Optimierung

### Phase 2 — Social Proof
- Social Proof Notification Banner (WhatsApp-Buchungen)
- Besucherzähler mit Ländern und Balken
- Zufällige Namen, Länder und Zeitangaben (Minuten + Stunden)

### Phase 3 — RevLink-System
- Partner Referral Links (`?wa=` Parameter)
- Short-Code-Generierung
- Custom Domain `go.myimpactflow.ch`
- PDF-Download mit QR-Code
- Plattform-Tracking (`?src=linkedin/facebook/...`)
- ZIP-Download

### Phase 4 — Animationen & Polish
- Typewriter-Effekt auf Hero-Titel (3 Zeilen, letzte in Pink)
- Typewriter-Effekt auf Quote-Sektion (mit Tipp-Fehlern)
- Scroll-basierte Border-Animation auf Pain-Cards (conic-gradient)
- Scroll-basierte Border-Animation auf Promise-Cards
- Sequenzielles Erscheinen der Steps beim Scrollen
- Mobile Hero-Reorder (Badge → Bild → Titel)

### Phase 5 — Widget-Verbesserungen
- Close-Button (X) für Visitor Counter
- Magnet-Icon bei Snap (oben/unten)
- Stunden in Social Proof Notifications

### Phase 6 — Rechtliches & Cleanup
- Impressum: Adresse, Impact Flow als Vertretungsberechtigte Stelle
- Datenschutzerklärung: Adresse, Stand März 2026
- Footer: "Ref-Link Generator" statt "RevLink"
- Logo zentriert auf Mobile (alle Unterseiten)

---

## Deployment

```bash
# Änderungen pushen → GitHub Pages deployed automatisch
cd ~/Desktop/Alle\ Projeke/03_Experimente/whatsapp-funnel-landing
git add .
git commit -m "Beschreibung"
git push origin main
```

**Live-URL:** `https://go.myimpactflow.ch`

---

## Lokale Entwicklung

```bash
# Preview-Server starten (Port 8081)
cd ~/Desktop/Alle\ Projeke/03_Experimente/whatsapp-funnel-landing
python3 -m http.server 8081

# Oder via Claude Code Preview (.claude/launch.json)
```

---

## Abhängigkeiten

Keine externen Dependencies. Alles ist Vanilla HTML/CSS/JS.

**Externe Ressourcen (CDN):**
- Google Fonts: `Playfair Display`, `Inter`
- jsPDF (via CDN) — PDF-Generierung in revlink.html
- QRCode.js (via CDN) — QR-Code in revlink.html
- JSZip (via CDN) — ZIP-Download in revlink.html

**Assets (GitHub):**
- Logos: `raw.githubusercontent.com/MyImpactFlow/impactflow-assets/main/logos/`
- Hero-Bild: `raw.githubusercontent.com/MyImpactFlow/impactflow-assets/main/images/`
