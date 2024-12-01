# Abrechnungsformular für den ADFC&nbsp;Hamburg

Dieser Code erstellt ein Docker-Image zum Starten eines einfachen Web&shy;servers. Dieser stellt ein Web&shy;formular bereit, auf dem Aktive und Helfer des ADFC&nbsp;Hamburg bequem die Details einer Geld&shy;abrechnung eintragen können. Aus den Angaben wird dann ein fertiges Abrechnungs&shy;formular als PDF-Datei erstellt, welche die Benutzer herunter&shy;laden können.

## Installation

> [!IMPORTANT]
> Docker muss auf dem System installiert sein.
> Für Einweisungen zu Docker [siehe hier](https://docs.docker.com/get-started/ "Get started with Docker").

Für Computer mit AMD64-Prozessor (wie den meisten modernen PCs) werden auf GitHub fertige Images als Pakete bereitgestellt. Das Aktuellste kann mit folgendem Befehl installiert werden:

```bash
docker pull ghcr.io/adfc-hamburg/abrechnungsformular:latest
```

Das Image lässt sich auch aus den Quelldateien erstellen. [Lade das Repository runter](https://github.com/ADFC-Hamburg/abrechnungsformular/archive/refs/heads/main.zip "Quellcode als zip-Datei") und entpacke es, dann führe im entpackten Ordner (mit der Datei ***Dockerfile***) folgenden Befehl aus:

```bash
docker build -t abrechnungsformular .
```

oder ersetze `.` durch den Pfad zum Ordner.

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
