# Abrechnungsformular für den ADFC&nbsp;Hamburg

Dieser Code erstellt ein Docker-Image zum Starten eines einfachen Web&shy;servers. Dieser stellt ein Web&shy;formular bereit, auf dem Aktive und Helfer des ADFC bequem die Details einer Geld&shy;abrechnung eintragen können. Aus den Angaben wird dann ein fertiges Abrechnungs&shy;formular als PDF-Datei mit eingebauter E-Rechnung erstellt, welche die Benutzer herunter&shy;laden können.

## Installation

> [!IMPORTANT]
> Docker muss auf dem System installiert sein.
> Für Einweisungen zu Docker [siehe hier](https://docs.docker.com/get-started/ "Get started with Docker").

### Vorgefertigte Version für den ADFC Hamburg

Für den ADFC Hamburg stehen für Computer mit AMD64-Prozessor (wie den meisten modernen PCs) auf GitHub fertige Images als Pakete bereit. Das Aktuellste kann mit folgendem Befehl installiert werden:
```bash
docker pull ghcr.io/adfc-hamburg/abrechnungsformular:latest
```

### Ein angepasstes Image erstellen

Ein angepasstes Docker-Image lässt sich aus den Quelldateien erstellen. [Lade dieses Repository runter](https://github.com/ADFC-Hamburg/abrechnungsformular/archive/refs/heads/main.zip "Quellcode als zip-Datei") und entpacke es in einen eigenen Ordner.

#### Namen und Kontaktdaten anpassen

Öffne im heruntergeladenen Repository die Datei **CONFIG.ini** und passe die Kontaktdaten an deinen Landesverband an.

#### Logo anpassen

Als Logo können entweder SVG- oder PNG-Dateien verwendet werden. Du benötigst folgende Datei:

* Eine Datei namens **logo.png** oder **logo.svg** - diese sollte eine farbige Version des Logos beinhalten.

Bei Verwendung von PNG außerdem benötigt, bei SVG optional:

  * Eine Datei namens **logo-semiwhite.png** oder **logo-semiwhite.svg** - bei dieser sollten zumindest die blauen Teile des Logos weiß gefärbt sein.
  * Eine Datei namens **logo-white.png**oder **logo-white.svg** - diese sollte eine weiße Version des Logos beinhalten.

Ersetze im Unterordner **static/img/** die Datei **logo.svg** durch die obigen Dateien.

> [!WARNING]
> Achte darauf, dass du nach dem Einfügen *entweder* PNG-Logos *oder* SVG-Logos im Ordner hast.

#### Das Image fertigstellen

Nach der Anpassung führe im entpackten Ordner (mit der Datei **Dockerfile**) folgenden Befehl aus:

```bash
docker build -t abrechnungsformular .
```

#### Das Image auf ein anderes Gerät übertragen

Bei Bedarf kann das erstellte Docker-Image auf ein anderes Gerät übertragen werden. Exportiere das Image mit folgendem Befehl:

```bash
docker save abrechnungsformular > abrechnungsformular.tar
```

Übertrage die so entstandene TAR-Datei auf das Zielgerät und führe dort im gleichen Ordner folgenden Befehl aus:

```bash
docker load < abrechnungsformular.tar
```

## Ausführung

Das Image aus dem GitHub-Paket wird mit folgendem Befehl gestartet:

```bash
docker run --rm -p 8000:8000 ghcr.io/adfc-hamburg/abrechnungsformular
```

Das aus den Quelldateien erstellte Image wird mit folgendem Befehl gestartet:

```bash
docker run --rm -p 8000:8000 abrechnungsformular
```

In beiden Fällen kann der Port des Servers gewählt werden, indem die erste Zahl in `-p 8000:8000` durch die gewünschte Portnummer ersetzt wird.
