# Space Shooter

Pygame-Shooter mit drei Gegnertypen, fünf Laser-Stufen, Drohnen,
Schild, Magnet und Smart-Bomb-Power-Ups.

## Auf dem Handy spielen

Die Browser-Version läuft mit pygbag/WebAssembly ohne Python-Installation
in einem aktuellen Safari (iPhone/iPad) oder Chrome (Android).
Beim ersten Öffnen lädt die Python-Laufzeit vom pygame-web-CDN; Internet
ist erforderlich. Querformat bietet das größte Spielfeld, Hochformat
wird mit unverzerrtem Seitenverhältnis angezeigt.

- Zum Starten auf die Seite und anschließend auf den Spielbildschirm tippen.
- Finger auf dem Spielfeld halten und ziehen: Schiff bewegen und automatisch feuern.
  Das Schiff bewegt sich relativ zum Finger, damit es sichtbar bleibt.
- Loslassen stoppt das Feuern. Ein zweiter Finger übernimmt die Steuerung nicht.
- Oben rechts: Pause. Zum Fortsetzen auf das Spielfeld tippen.
- Nach Game Over auf das Spielfeld tippen, um neu zu starten.
- Beim Fokusverlust pausiert das Spiel.

## Veröffentlichung über GitHub Pages

1. Diese Änderungen in `main` übernehmen.
2. Im Repository unter **Settings → Pages → Build and deployment → Source**
   **GitHub Actions** auswählen (einmalig).
3. Den Workflow **Mobile browser build** ausführen bzw. den Build nach dem
   Merge abwarten.

Der Workflow testet die Touch-Steuerung, erstellt den Web-Build und
veröffentlicht ihn von `main` auf GitHub Pages. Die endgültige URL steht
im Deployment; normalerweise: https://miew666.github.io/SpaceShooter/

Pull Requests und der Branch `mobile-browser` bauen nur ein herunterladbares
Artefakt und veröffentlichen noch nichts.

## Lokal starten

Desktop (Pfeiltasten, Leertaste, P/Enter für Pause, R für Neustart, Esc beendet):

```sh
python -m pip install -r requirements.txt
python main.py
```

Browser-Vorschau:

```sh
python -m pip install -r requirements-web.txt
mkdir -p webapp
cp *.py webapp/
cp -R graphics webapp/
python -m pygbag --template web/mobile.tmpl --title "Space Shooter" webapp
```

Dann http://localhost:8000 öffnen. Auf einem Handy einen vom Rechner
erreichbaren HTTP-Server bzw. den veröffentlichten HTTPS-Link benutzen.
Die HTML-Datei nicht direkt als `file://` öffnen.

Headless-Tests:

```sh
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m unittest discover -s tests -v
```

Die mobile HTML-Vorlage basiert auf der pygbag-0.9.2-Standardvorlage.
Grafiken und deren Lizenz stehen in `graphics/license.txt`.
