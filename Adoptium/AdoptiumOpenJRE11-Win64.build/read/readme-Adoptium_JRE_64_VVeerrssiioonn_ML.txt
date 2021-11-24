Adoptium Open JRE x64 11.0.100.1 ML (Multi-Language)
Java Runtime Environment for x64 Windows.
Adoptium is the successor of AdoptOpenJDK.
1:1 substitution for Oracle JavaRE

Tested on Windows 10

Optional features:
FeatureJarFileRunWith	Associate .jar files to run with Eclipse Temurin
FeatureJavaHome		Set JAVA_HOME environment variable.
FeatureOracleJavaSoft	Overwrites the reg keys HKLM\Software\JavaSoft (Oracle).
FeatureJavaFX		Install JavaFX.

To install an additional feature, add ADDLOCAL=feature1,feature2..

To install all features to a machine, use this command:
msiexec /i "Adoptium_JRE_Hotspot_64_11.0.100.0_ML.msi" ALLUSERS=1 ADDLOCAL=ALL

Slient Install: msiexec /i "Adoptium_JRE_Hotspot_64_11.0.100.0_ML.msi" /qn (absolute silent) or /qb! (with progress-dialog).

All MSI-versions from Adopt are found and automatically removed. Only one version can be installed.

Features in this version:
- Multi-Language enu, deu, fra.
- JavaFX support.

Release 1.0, Build 1
20191115, by AutoPkg