Adoptium IcedTea-Web 1.1.1.1 ML (Multi-Language)
1:1 substitution for Oracle Webstart.

Tested on Windows 10

To install all features to a machine, use this command:
msiexec /i "Adoptium_IcedTea-Web_64_1.0.1.0_ML.msi" ALLUSERS=1 ADDLOCAL=ALL

Slient Install: msiexec /i "Adoptium_IcedTea-Web_64_1.0.1.0_ML.msi" /qn (absolute silent) or /qb! (with progress-dialog).

Watch out for downloads from web-addresses that are not TLS secured.
You need to explicitly set the commandline like this:
javaws.exe -property deployment.https.noenforce=true -jnlp <JNLPfile>.jnlp

Release 1.0, Build 1
20191115, Nick Heim
