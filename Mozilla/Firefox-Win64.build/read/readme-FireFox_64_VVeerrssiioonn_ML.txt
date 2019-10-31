Mozilla Firefox x64 66.0.2 ML (Multi-Language)

Webbrowser. Alternative zu Internet-Explorer.

Getestet mit Windows 7, 8.1 + 10

Neuheiten in dieser Version: 	keine.

Mozilla Release Notes zu FF 66.0.2: https://www.mozilla.org/en-US/firefox/66.0.2/releasenotes/

Optionen: - DEFAULTPREFS=0   --> Default-Prefs können ausgeschaltet werden. Siehe auch create-log.
	  - DESKTOP_SC=0     --> Shortcuts auf dem Desktop können ausgeschaltet werden.
	  - PROFMIGR=0	     --> Der Profile Migration Wizard kann ausgeschaltet werden.

Dazu die Installation mit folgender Kommandozeile starten:
msiexec /i "FireFox_64_66.0.2_ML.msi" DESKTOP_SC=0 QUICKLAUNCH_SC=0 DEFAULTPREFS=0
Achtung: Der Desktop Shortcut wird in den AllUsers Bereich, der QuickLaunch Shortcut in den Benutzer Bereich installiert.

Slient Install: msiexec /i "FireFox_64_66.0.2_ML.msi" /qn (komplett silent) oder /qb! (mit Fortschritts-Dialog).

Alle ETH Versionen 1.01, 1.07, 1.5.0.1 + 1.5.0.4, 1.5.0.6, 2.0.0.x, 3.x, 5-66.x werden erkannt und automatisch deinstalliert.

Features in dieser Version:
- Multi-Language enu, deu, fra, ita, rum (rätoromanisch).
- Spellchecker für enu, deu, fra, ita.
- Firefox-Sprache folgt automatisch der System-Sprache auch beim Multi-Language-Pack.
- alle Settings per Group Policies konfigurierbar.
- Zusätzliche Search-Plugins für: ETH-Phonebook, NEBIS-/Swissbib-Bibliotheks-Abfrage.
   Sowie für: local.ch, map.search.ch, anibis.ch, ricardo.ch, toppreise.ch
- Flashplayer Plugin wird automatisch integriert, wenn im System vorhanden.
- NoScript, Ausführen von JavaScript und aktiven Inhalten nur bei vertrauenswürdigen Sites erlauben.
- Mit rätoromanischer Oberfläche.
- Mit Adblock Plus Erweiterung.
- CAcert Zertifikate werden beim Erstellen eines neuen Profils automatisch eingebunden.
- Abschalten von Application reputation checks via Google Safe Browsing API.
- Single Sign on in ETH Intranet (nur bei neuem Profil).
- Click to Play für PDF und WMP ausgeschaltet.


Release 1.0, Build 1
20190401, Nick Heim
