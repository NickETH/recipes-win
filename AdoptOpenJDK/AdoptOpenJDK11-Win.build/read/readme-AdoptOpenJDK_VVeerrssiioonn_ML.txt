Adopt Open JDK x86 8.0.100.0 ML (Multi-Language)
Java Development Kit for x86 Windows.
1:1 substitution for Oracle JavaDK, but no Webstart (only availabel in x64).

Tested on Windows 7, 8.1 + 10

Optional features:
FeatureEnvironment	Add to PATH environment variable.
FeatureJarFileRunWith	Associate .jar files to run with AdoptOpenJDK
FeatureJavaFX		Install JavaFX
FeatureJavaHome		Set JAVA_HOME environment variable.
FeatureOracleJavaSoft	JavaSoft (Oracle) registry keys	Overwrites the reg keys HKLM\Software\JavaSoft (Oracle).
To install an additional feature, add ADDLOCAL=feature1,feature2...

To install all features to a machine, use this command:
msiexec /i "AdoptOpenJDK_Hotspot_8.0.100.0_ML.msi" ALLUSERS=1 ADDLOCAL=ALL

Slient Install: msiexec /i "AdoptOpenJDK_Hotspot_8.0.100.0_ML.msi" /qn (absolute silent) or /qb! (with progress-dialog).

All MSI-versions from Adopt are found and automatically removed. Only one version can be installed.

Features in this version:
- Multi-Language enu, deu, fra.
- JavaFX support.

Release 1.0, Build 1
20190101, Nick Heim
