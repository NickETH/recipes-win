@ECHO OFF

REM Change version numbers here:
SET PRODUCT_MAJOR_VERSION=3
SET PRODUCT_MINOR_VERSION=45
SET PRODUCT_MAINTENANCE_VERSION=1
SET PRODUCT_PATCH_VERSION=0



:: Hash erzeugen
cscript.exe /B /NoLogo hash2.vbs %cd%fzputtygen.exe
:: ergibt: MsiFileHash.idt
MOVE /Y .\MsiFileHash.idt MsiFileHash.id1
:: Hash erzeugen
cscript.exe /B /NoLogo hash2.vbs fzsftp.exe
:: ergibt: MsiFileHash.idt


:: Temporäres MSI-File erstellen.
msidb -c -f%cd% -d ReleaseDir\MergeHash1.msi *
:: Temporäres MSI-File in Haupt-MSI-File mergen.
msidb -mReleaseDir\MergeHash1.msi -d ReleaseDir\!OUTPUT_BASE_FILENAME!.msi

MOVE /Y .\MsiFileHash.id1 MsiFileHash.idt

:: Temporäres MSI-File erstellen.
msidb -c -f%cd% -d ReleaseDir\MergeHash2.msi *
:: Temporäres MSI-File in Haupt-MSI-File mergen.
msidb -mReleaseDir\MergeHash2.msi -d ReleaseDir\!OUTPUT_BASE_FILENAME!.msi

cscript.exe /B /NoLogo WiRunSQL.vbs ReleaseDir\!OUTPUT_BASE_FILENAME!.msi "UPDATE `File` SET `File`.`Version`=NULL WHERE `File`.`File`='fzputtygen.exe'"
cscript.exe /B /NoLogo WiRunSQL.vbs ReleaseDir\!OUTPUT_BASE_FILENAME!.msi "UPDATE `File` SET `File`.`Version`=NULL WHERE `File`.`File`='fzsftp.exe'"

REM )
ENDLOCAL

REM Clean ProjectFiles
DEL /Q ReleaseDir\MergeHash1.msi
DEL /Q ReleaseDir\MergeHash2.msi
DEL /Q ReleaseDir\*.wixpdb
DEL /Q MsiFileHash.idt
DEL /Q "Files-"*.wxs
DEL /Q *.wixobj

REM Cleanup variables
SET CULTURE=
SET LANGIDS=
