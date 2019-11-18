Adopt Open JRE x86 11.0.100.1 ML (Multi-Language)
Java Runtime Environment for x64 Windows.
1:1 substitution for Oracle JavaRE

Tested on Windows 10

Optionen: - ADDLOCAL=ALL   --> notwendig für eine vollständige Installation. Siehe auch create-log.

Dazu die Installation mit folgender Kommandozeile starten:
msiexec /i "AdoptOpenJDK_JRE_Hotspot_11.0.1.1_ML.msi" ADDLOCAL=ALL

Slient Install: msiexec /i "AdoptOpenJDK_JRE_Hotspot_11.0.1.1_ML.msi" /qn (absolute silent) or /qb! (with progress-dialog).

All MSI-versions from Adopt are found and automatically removed. Only one version can be installed.

Features in dieser Version:
- Multi-Language enu, deu, fra.
	(noch nicht implementiert) - Webstart.
- JavaFX support.

Release 1.0, Build 1
20190101, Nick Heim
