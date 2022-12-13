# Powermeter logger (Micropython)
Software um die aktuellen Messwerte verschiedener Energiemessdosen auszulesen und an einen externen Webserver weiterzuleiten. Dort können sie zur weiteren Verarbeitung geloggt werden.

## Unterstützte Hardware
* Wemos D1 Mini (ESP8266)
* Theoretisch alle weiteren Geräte auf denen Micropython läuft

## Unterstützte Energiemessdosen
* Fritz!DECT 200/210
* Shelly-Geräte (getestet: Shelly Plug S, Shelly 1 PM)

## Installation / Konfiguration
1. Micropython flashen: https://docs.micropython.org/en/latest/esp8266/tutorial/intro.html
1. Mit der REPL verbinden und WebREPL aktivieren https://docs.micropython.org/en/latest/esp8266/tutorial/repl.html
1. WebREPL herunterladen: https://github.com/micropython/webrepl
1. Mit dem WLAN-AP verbinden (MicroPython-xxxxxx / micropythoN)
1. WebREPL starten und mit folgenden Daten verbinden: ws://192.168.4.1:8266
1. Mit zuvor gewähltem Passwort einloggen und alle Dateien aus diesem Repository auf das Gerät hochladen (idealerweise Konfiguration in der Datei "powermeter_cfg.py" vorher anpassen)
1. Gerät neu starten
1. Mit dem WLAN-AP verbinden (WiFiManager / wifimanager), siehe auch: https://github.com/ferreira-igor/micropython-wifi_manager
1. Im Browser http://192.168.4.1 öffnen und Gerät mit eigenem WLAN verbinden
1. ggf. WebREPL mit neuer IP und Port 8266 verbinden um Dateien anzupassen

## Dokumentation Boot bzw. LED-Anzeige
1. Direkt nach dem Booten blinkt die LED 20x pro Sekunde und der WiFi-Manager wird ausgeführt
1. Sobald das Gerät sich erfolgreich mit einem WLAN verbunden hat blinkt es 1x pro Sekunde
1. Tritt ein Fehler beim Laden der Konfigurationsdatei auf blinkt die LED 2x pro Sekunde
1. Während die Daten aus der Energiemessdose ausgelesen und an den Server übermittelt werden blinkt die LED 5x pro Sekunde
1. Alle 10 Durchläufe wird die Uhrzeit synchronisiert, dabei blinkt die LED 10x pro Sekunde
1. Nach (maximal) 10 Sekunden Wartezeit beginnt die Routine wieder bei Punkt 4

## Datenübermittlung an externen Webserver
* Übermittlung per HTTPS an log.php
* Übermittelte Parameter:
1. 'key' (der übermittelte Schlüssel muss auf Server und Client übereinstimmen, damit nicht jeder "einfach so" Daten übermitteln kann)
1. 'stats' (kommaseparierter String im Format "Datum,Uhrzeit,Leistung[,Temperatur]" - jeweils ohne Einheit)

## Credits / verwendete Bibliotheken
* WiFi Manager von https://github.com/ferreira-igor/micropython-wifi_manager
* MD5-Bibliothek von https://github.com/lemariva/ESP32MicroPython
