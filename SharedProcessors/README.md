Nick's Shared processors for AutoPkg.win
========================================

Recipes for AutoPkg on Windows

AcrobatGUIDPatcher
------------------
Creates a new GUID for Adobes Acrobat Pro DC and Reader DC.
This is needed, if this products are patched offline.
```
Input variables:
base_GUID, (required: True), Description: "GUID of the product's base version, required."
new_ver, (required: True), Description: "Version string, to patch into the GUID, required."
old_hex_ver, (required: True), Description: "Old hex version string to exchange, required."
ignore_errors, (required: False), Description: "Ignore any errors during the run."
Output variables:
newGUID, Description: "New GUID."
```
	
CreateNextBuild
---------------
Set up a build environment for a given package.
Create folders, copy needed files from repository and/or previous build.
```
Input variables:
build_dir, (required: True), Description: "Path to the build dir".
recipe_dir, (required: True), Description: "Path to the recipe_dir."
org_ver, (required: True), Description: "Original version string."
pkg_dir, (required: True), Description: "Path to the pkg_dir, if the tag ::VVeerrssiioonn:: is part of, it will be replaced with the normalized version."
folder_list, (required: True), Description: "Path to the folder_list."
ver_fields, (required: False), Description: "Number of version fields divided by periods."
create_AS_ver, (required: False), Description: "Bool, Create a version string for an Active Setup."
recipe_path, (required: False), Description: "Path to the recipe file."
BuildFiles, (required: False), Description: "Textfile, containing the paths to the additional buildfiles to copy."
recipe_cache_dir, (required: False), Description: "Path to the recipe cache dir."
PrevVerFiles, (required: False), Description: "Textfile, containing the paths to files needed from the previous build."
ignore_errors, (required: False), Description: "Ignore any errors during the run."
Output variables:
build_ver, Description: "Normalized version string."
build_ver_short, Description: "Special version string without dots."
AS_ver, Description: "Special version string for an Active Setup."
```

DateTimeStamps
--------------
Returns date and time in variables.
```
Output variables:
us_date, Description: "Actual date in US style."
year, Description: "Actual year."
month, Description: "Actual month."
day, Description: "Actual day."
time, Description: "Actual time."
```

ExeVersionExtractor
-------------------
Extracts version info from .exe file using the 7z utility.
Deprecated! Use WinPEVersionExtractor instead.
```
Input variables:
exe_path, (required: False), Description: "Path to exe or msi, defaults to %pathname%."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."
Output variables:
version, Description: "ProductVersion of exe found." 
```

FileDateVersionSubst
--------------------
Load a text file and search for date and version patterns and actualize them.
```
Input variables:
file_path, (required: True), Description: "Path to a file to update."
new_ver, (required": False), Description: "New version string to write."
re_pattern, (required: True), Description: "Regular expression of version string to replace."
```

MSIApplySumInfo
---------------
Apply (multiple) summary info changes to MSI-file using msiinfo.exe.
```
Input variables:
msi_path, (required: True), Description: "Path to the msi."
cmnds_sinfo, (required: True), Description: "Dict of Suminfo commands to execute. Pairs of key(flag)/string are expected."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."
```

MSIApplyTransform
-----------------
Apply transform(s) to an MSI-file using msitran.exe.
Deprecated! Use MSITransformer instead.
```
Input variables:
msi_path, (required: True), Description: "Path to the msi."
mst_paths, (required: True), Description: "(Array of) Paths to the mst."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."
```

MSIDbWorker
-----------
Wrapper around msidb.exe to work with an MSI-file.
```
Input variables:
mode, (required: True), Description: "Mode of working (-e,-i,-m,-a,-r,-t,-j,-k,-x,-w)."
msi_path, (required: True), Description: "Path to the msi."
workfile, (required: False), Description: "Path to the file to work with (stream, storage, msi, transform)."
workfolder, (required: False), Description: "Path to the folder, where files should be written or read; Or the folder to work with table text files."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."
```

MSITransformer
--------------
Generate or Apply transform(s) to/from (an) MSI-file(s) using msitran.exe.
```
Input variables
mode, (required: False), Description: "Mode of working -a/-g (Apply/Generate), defaults to '-a'."
msi_path, (required: True), Description: "Path to the msi."
msi_path_new, (required: False), Description: "Path to the new changed msi, when generating an MST."
mst_paths, (required: True), Description: "(Array of) path(s) to the mst (on Apply) or output mst, when generating."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."
```

MSIimportMergeModule
--------------------
Import a MergeModule into a MSI file.
```
Input variables:
pkg_dir_abs, (required: True), Description: "Absolute path to the pkg_dir."
msi_path, (required: True), Description: "Path to the MSI-file, relative to pkg_dir."
msm_path, (required: True), Description: "Path to the MSM-file, relative to pkg_dir."
msm_feature, (required: True), Description: Feature in the MSI-file to connect the MSM to."
msm_dir, (required: True), Description: "Directory in the MSI-file to install the MSM, required."
temp_path, (required: False), Description: "Path to store the temporary build files."
log_file_abs, (required: False), Description: "Absolute path to the merge log file."
ignore_errors, (required: False), Description: "Ignore any errors during the run."
```

MSIofflinePatcher
-----------------
Apply an patch to an MSI file offline and rebuild the package (compression of files on or off). Can also compact an MSI.
```
Input variables:
pkg_dir_abs, (required: True), Description: "Absolute path to the pkg_dir."
msi_path, (required: True), Description: "Path to the MSI-file, relative to pkg_dir."
msp_path, (required: False), Description: "Path to the MSP-file, relative to pkg_dir, omit for cabs in or compress only."
compact_msi, (required: False), Description: "Compact the MSI-file."
adm_msi_path, (required: True), Description: "Path to the MSI-file to be patched, relative to pkg_dir."
new_msi_path, (required: True), Description: "Path to the new MSI-file, relative to pkg_dir."
cab_file, (required: True), Description: "Name of the CAB-file to generate."
cab_dir, (required: False), Description: "Folder where the CAB-file should be generated, relative to pkg_dir."
embed_cab, (default: False, required: False), Description: "Embed the cabinet file in the MSI-file".
new_packcode, (default: False, required: False), Description: "Set a new packagecode in the MSI-file."
ignore_errors, (required": False), Description: "Ignore any errors during the run."
```

MSIRunSQL
---------
Run a(n) (array of) SQL-Command(s) against an MSI-file.
```
Input variables:
msi_path, (required: True), Description: "Path to the msi."
SQL_command, (required: True), Description: "(Array of) SQL command(s) to run."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."
```

MSIRunSQLget
------------
Run an SQL-Command SELECT against an MSI-file.
```
Input variables:
msi_path, (required: True), Description: "Path to the msi."
SQL_command, (required: True), Description: "SQL command to run."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."
Output variables:
msi_value, Description: "Value from the SQL run."
```

NANTrun
-------
Run NANT to build a NANT-(WIX-)project or to call a specific NANT-command.
```
Input variables:
run_folder, (required: True), Description: "Path to the (WIX) build dir."
build_target, (required: False), Description: "Target to run in NANT-file."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."
```

ResourceExtractor
-----------------
Extracts a resource from a Windows exe using ResourceHacker.
```
Input variables:
exe_path, (required: False), Description: "Path to the (setup.)exe, defaults to %pathname%."
extract_dir, (required: True), Description: "Output path (absolute) for the extracted archive."
extract_file, (required: True), Description: "Output filename of the resource to be extracted."
extract_cmd, (required: True), Description: "Resource to extract (e.g. 'BIN,123,')."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."
Output variables:
version, Description: "Version of exe found."
```

SevenZipExtractor
-----------------
Extracts specific file(s) using the 7z utility.
```
Input variables:
exe_path, (required: False), Description: "Path to exe or msi, defaults to %pathname%."
preserve_paths, (required: False), Description: "Extract archive with full paths, defaults to 'True'."
extract_dir, (required: True), Description: "Output path for the extracted archive."
extract_file, (required: False), Description: "File to be extracted or a @listfile.txt."
ignore_pattern, (required: False), Description: "Wildcard pattern to ignore files from the archive."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."
```

TextFileSearch
--------------
Reads a text file and looks for a regex pattern and returns the string that matched the pattern.
```
Input variables:
file_to_open, (required: True), Description: "The text file that needs to be opened for reading."
pattern, (required: True), Description: "The regex pattern to look for and return."
Output variables:
matchstring, Description: "Returns the string that matched the pattern."
        }
WinPEVersionExtractor
---------------------
Extracts version info from Windows PE-executable (.exe/.dll) file.
```
Input variables:
exe_path, (required: False), Description: "Path to exe or msi, defaults to %pathname%."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."
Output variables:
version, Description: "Version of exe found."
```

WixDefaults
-----------
Create version and default property files (version.wxi, global.prop) for the next NANT-(WIX-)build."
```
Input variables:
build_dir, (required: True), Description: "Path to the build_dir, required",
build_ver, (required: True), Description: "Version string, that we are using to build the package."
org_ver, (required: False), Description: "Original version string."
ignore_errors, (required: False), Description: "Ignore any errors during the run."
```