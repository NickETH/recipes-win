Nick's Shared processors for AutoPkg.win
========================================

Recipes for AutoPkg on Windows

AcrobatGUIDPatcher
------------------
Creates a new GUID for Adobes Acrobat Pro DC and Reader DC.
This is needed, if this products are patched offline.
Input variables:
base_GUID, (required: True), Description: "GUID of the product's base version, required."
new_ver, (required: True), Description: "Version string, to patch into the GUID, required."
old_hex_ver, (required: True), Description: "Old hex version string to exchange, required."
ignore_errors, (required: False), Description: "Ignore any errors during the run."
Output variables:
newGUID, Description: "New GUID."
			
CreateNextBuild
---------------
Set up a build environment for a given package.
Create folders, copy needed files from repository and/or previous build.
Input variables:
build_dir, (required: True), Description: "Path to the build dir".
recipe_dir, (required: True), Description: "Path to the recipe_dir."
org_ver, (required: True), Description: "Original version string."
pkg_dir, (required: True), Description: "Path to the pkg_dir, if the tag ::VVeerrssiioonn:: is part of, it will be replaced with the normalized version."
folder_list, (required: True), Description: "Path to the folder_list."
ver_fields, (required: False), Description: "Number of version fields divided by periods."
recipe_path, (required: False), Description: "Path to the recipe file."
BuildFiles, (required: False), Description: "Textfile, containing the paths to the additional buildfiles to copy."
recipe_cache_dir, (required: False), Description: "Path to the recipe cache dir."
PrevVerFiles, (required: False), Description: "Textfile, containing the paths to files needed from the previous build."
ignore_errors, (required: False), Description: "Ignore any errors during the run."
Output variables:
build_ver, Description: "Normalized version string."


DateTimeStamps
--------------
Returns date and time in variables.
Output variables:
us_date, Description: "Actual date in US style."
year, Description: "Actual year."
month, Description: "Actual month."
day, Description: "Actual day."
time, Description: "Actual time."

ExeVersionExtractor
-------------------
Extracts version info from .exe file using the 7z utility.
Slightly changed version of "ExeVersionExtractor" by Matt Hansen.
Input variables:
exe_path, (required: False), Description: "Path to exe or msi, defaults to %pathname%."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."
Output variables:
version, Description: "ProductVersion of exe found." 
			
FileDateVersionSubst
--------------------
Load a file and search for date and version patterns and actualize them.
Input variables:
file_path, (required: True), Description: "Path to a file to update."
new_ver, (required": False), Description: "New version string to write."
re_pattern, (required: True), Description: "Regular expression of version string to replace."

MSIApplySumInfo
---------------
Apply (multiple) summary info changes to MSI-file using msiinfo.exe.
Input variables:
msi_path, (required: True), Description: "Path to the msi."
cmnds_sinfo, (required: True), Description: "Dict of Suminfo commands to execute. Pairs of key(flag)/string are expected."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."

MSIApplyTransform
-----------------
Apply transform(s) to an MSI-file using msitran.exe.
Input variables:
msi_path, (required: True), Description: "Path to the msi."
mst_paths, (required: True), Description: "(Array of) Paths to the mst."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."

MSIofflinePatcher
-----------------
Apply an patch to an MSI file offline and rebuild the package.
Input variables:
pkg_dir_abs, (required: True), Description: "Absolute path to the pkg_dir."
msi_path, (required: True), Description: "Path to the MSI-file, relative to pkg_dir."
msp_path, (required: True), Description: "Path to the MSP-file, relative to pkg_dir."
adm_msi_path, (required: True), Description: "Path to the MSI-file to be patched, relative to pkg_dir."
new_msi_path, (required: True), Description: "Path to the new MSI-file, relative to pkg_dir."
cab_file, (required: True), Description: "Name of the CAB-file to generate."
cab_dir, (required: False), Description: "Folder where the CAB-file should be generated, relative to pkg_dir."
embed_cab, (default: False, required: False), Description: "Embed the cabinet file in the MSI-file".
new_packcode, (default: False, required: False), Description: "Set a new packagecode in the MSI-file."
ignore_errors, (required": False), Description: "Ignore any errors during the run."

MSIRunSQL
---------
Run a(n) (array of) SQL-Command(s) against an MSI-file.
Input variables:
msi_path, (required: True), Description: "Path to the msi."
SQL_command, (required: True), Description: "(Array of) SQL command(s) to run."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."

MSIRunSQLget
------------
Run an SQL-Command SELECT against an MSI-file.
msi_path, (required: True), Description: "Path to the msi."
SQL_command, (required: True), Description: "SQL command to run."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."
Output variables:
msi_value, Description: "Value from the SQL run."

NANTrun
-------
Run NANT to build a NANT-(WIX-)project or to call a specific NANT-command."
run_folder, (required: True), Description: "Path to the (WIX) build dir."
build_target, (required: False), Description: "Target to run in NANT-file."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."

RenameVar
---------
Substitute a character from a given string and return the parsed string
Copied version of "RenameVar" by Sebastien Tomasi.
Input variables:
input_var, (required: True), Description: "Name of the variable to rename."
rename_var, (required: True), Description: "Name of the variable to copy the value to."

SevenZipExtractor
-----------------
Extracts specific file(s) using the 7z utility.
Input variables:
exe_path, (required: False), Description: "Path to exe or msi, defaults to %pathname%."
preserve_paths, (required: False), Description: "Extract archive with full paths, defaults to 'True'."
extract_dir, (required: True), Description: "Output path for the extracted archive."
extract_file, (required: False), Description: "File to be extracted or a @listfile.txt."
ignore_pattern, (required: False), Description: "Wildcard pattern to ignore files from the archive."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."

WixDefaults
-----------
Create version and default property files (version.wxi, global.prop) for the next NANT-(WIX-)build."
Input variables:
build_dir, (required: True), Description: "Path to the build_dir, required",
build_ver, (required: True), Description: "Version string, that we are using to build the package."
org_ver, (required: False), Description: "Original version string."
ignore_errors, (required: False), Description: "Ignore any errors during the run."
