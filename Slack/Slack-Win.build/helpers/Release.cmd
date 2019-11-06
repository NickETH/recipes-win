:: Dateien auf den Release-Share kopieren.

::	Aktuelles Verzeichnis in Variable HELPERDIR
cd > helperdir.txt
set /p HELPERDIR= < helperdir.txt
set /p filever=<FFFilever.txt
echo %filever%
:: Create the long version string. A Major Version has only 2 digits in the version info, but we need 3 in most version strings.
set ShortverMid=%filever:*.=%
set ShortverEnd=%ShortverMid:*.=%
IF %ShortverEnd% == %ShortverMid% (
	set filever=%filever%.0
) ELSE (
	set filever=%filever%
)
echo %filever%

set verstring=%filever:.=%0
set verstring=%verstring:~0,4%
set majorver=%filever:~0,2%
echo %filever%-%verstring%-%majorver%
set NASPATH=\\d\SYS\win\pkg\sec\iia1
set DESTDIR=FireFox_%majorver%.x_ML
set DESTPATH=%NASPATH%\%DESTDIR%
pause
md %DESTPATH%
set ReleaseFilesSet="FireFox_%filever%_ML.msi ALL-enu-deu-%verstring%.mst AllFeatures-%verstring%.mst ID-BI-mini-%verstring%.mst NoDefPrefs-%verstring%.mst NoDQSC-%verstring%.mst STUD-ML-%verstring%.mst Adblk-ML-%verstring%.mst"
set ReleaseFilesSet=%ReleaseFilesSet:"=%
pause

cd %HELPERDIR%

copy ..\howtopkt\create-log*.txt %DESTPATH%\
copy ..\infopkt\readme-*.txt %DESTPATH%\
FOR %%G IN (%ReleaseFilesSet%) DO copy ..\testmsi\%%G %DESTPATH%\%%G


set filever=
set verstring=
set ReleaseFilesSet=
set HELPERDIR=
set NASPATH=
set DESTDIR=
set DESTPATH=
