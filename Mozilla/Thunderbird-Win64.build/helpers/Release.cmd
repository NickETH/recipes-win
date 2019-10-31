:: Dateien auf den Release-Share kopieren.

::	Aktuelles Verzeichnis in Variable HELPERDIR
cd > helperdir.txt
set /p HELPERDIR= < helperdir.txt
set /p filever=<TBFilever.txt
set verstring=%filever:.=%0
set verstring=%verstring:~0,4%
set majorver=%filever:~0,2%
echo %filever%-%verstring%-%majorver%
set NASPATH=\\d.ethz.ch\SYS\win\pkg\sec\iia1
set DESTDIR=Thunderbird_64_%majorver%.x_ML
set DESTPATH=%NASPATH%\%DESTDIR%
pause
md %DESTPATH%
set ReleaseFilesSet="ThunderBird_*_ML.msi TB-All-%verstring%_ED.mst TB-All-%verstring%.mst"
set ReleaseFilesSet=%ReleaseFilesSet:"=%
pause

cd %HELPERDIR%

copy ..\howtopkt\create-log*.txt %DESTPATH%\
copy ..\infopkt\readme-*.txt %DESTPATH%\
::FOR %%G IN (%ReleaseFilesSet%) DO copy ..\testmsi\%%G %DESTPATH%\%%G
copy ..\testmsi\*.msi %DESTPATH%\
copy ..\testmsi\*.mst %DESTPATH%\

set filever=
set verstring=
set ReleaseFilesSet=
set HELPERDIR=
set NASPATH=
set DESTDIR=
set DESTPATH=
