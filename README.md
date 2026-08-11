# Abrechnungsformular für den ADFC&nbsp;Hamburg

Dieser Code erstellt ein Docker-Image zum Starten eines einfachen Web&shy;servers. Dieser stellt ein Web&shy;formular bereit, auf dem Aktive und Helfer des ADFC bequem die Details einer Geld&shy;abrechnung eintragen können. Aus den Angaben wird dann ein fertiges Abrechnungs&shy;formular als PDF-Datei mit eingebauter E-Rechnung erstellt, welche die Benutzer herunter&shy;laden können.

## Installation

> [!IMPORTANT]
> Docker (und optional Docker Compose) müssen auf dem System installiert sein.
> Für Einweisungen zu Docker [siehe hier](https://docs.docker.com/get-started/ "Get started with Docker").

Auf GitHub stehen fertige Images als Pakete bereit. Diese verwenden standardmäßig die Kontaktdaten und Logos des _ADFC_&nbsp;_Hamburg_, können jedoch nach Belieben angepasst werden. Das aktuellste Image kann mit folgendem Befehl heruntergeladen werden:
```bash
docker pull ghcr.io/adfc-hamburg/abrechnungsformular:latest
```

## Ausführung

Der einfachste Weg, das Docker-Image auszuführen, ist mit Docker Compose. Hierzu wird eine Compose-Datei benötigt; eine vorgefertigte Compose-Datei [findet sich hier](samples/docker-compose.yml).

Mit folgendem Befehl kann der Webserver im Hintergrund gestartet werden:

```bash
docker compose -f pfad/zur/docker-compose.yml up --detach
```

Mit folgendem Befehl wird der Webserver wieder beendet:

```bash
docker compose -f pfad/zur/docker-compose.yml down
```

Die bereitgestellte Compose-Datei ist so eingestellt, dass der Server bei Systemneustart ebenfalls gestartet wird, bis er manuell beendet wird. Ist dieses Verhalten unerwünscht, kann aus der Compose-Datei die Zeile `restart: unless-stopped` entfernt werden.

## Anpasssung

### Portnummer

Die Portnummer, unter der der Webserver erreichbar ist, kann gewählt werden, indem die erste Zahl in der Zeile `- 8000:8000` durch die gewünschte Portnummer ersetzt wird.

### Kontaktdaten und Pauschalen

Zum Abändern der Kontaktdaten sowie der Reisekosten&shy;pauschalen wird eine Kopie der [Config-Datei](CONFIG.ini) benötigt. Nachdem die Werte und Angaben in dieser Kopie angepasst wurden, kann sie in das Docker-Image eingebunden werden. Hierzu wird in der Compose-Datei das **#**-Symbol in folgenden Zeilen entfernt:

```docker-compose.yml
    volumes:
      - /pfad/zur/CONFIG.ini:/abrechnungsformular/CONFIG.ini
```

Der `/pfad/zur/CONFIG.ini` muss dabei natürlich angepasst werden. Sollte der Webserver bereits laufen, muss er neu gestartet werden, damit die Änderungen wirksam werden.

### Logos

Das Logo des Verbandes sollte idealerweise in drei Versionen vorhanden sein: eine reguläre Version, eine Version ohne die Farbe Blau für die Webseite, sowie eine vollständig schwarze Version. Alle gängigen Bildformate werden unterstützt.

Die zu verwendenden Logos müssen auf dem Docker-Image eingebunden werden. Hierzu wird in der Compose-Datei das #-Symbol in folgenden Zeilen entfernt:

```docker-compose.yml
    volumes:
      - /pfad/zum/logo.png:/abrechnungsformular/static/img/logo.png
```

Der `/pfad/zum/logo.png` und der Dateiname `logo.png` müssen dabei angepasst werden. Um mehrere Dateien einzubinden, kann die Zeile mit den Pfaden dupliziert werden. Alternativ kann auch ein Ordner mit den Logos eingebunden werden (z.B. `/pfad/zum/ordner:/abrechnungsformular/static/img/ordner`).

Zuletzt müssen in der Config-Datei ([siehe oben](#kontaktdaten-und-pauschalen)) die korrekten Dateinamen eingefügt werden. Bei Einbinden eines Odners muss auf diesen verwiesen werden (z.B. `unterordner/logo.png`). Sollte eine der oben genannten Versionen des Logos fehlen, kann eine andere Version als Ersatz mehrfach verwendet werden.