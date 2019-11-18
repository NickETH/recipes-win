:: Clean the directories from temp files. Move the package files to stable. Zip the project to an archive.
:: echo on
set SEVENZIP="C:\Program Files\7-Zip\7z.exe"
:: move /-y ..\testmsi\*.ms? ..\stablemsi\
cd ..\wixproject
cmd.exe /c nant clean
cd ..
for %%a in (.) do set currentfolder=%%~nxa
echo %currentfolder%
set workfolder=%CD%
cd ..
%SEVENZIP% a %currentfolder%.zip %workfolder%
