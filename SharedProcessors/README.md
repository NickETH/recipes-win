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

BMSImporter
-----------
Import a new application into BMS (baramundi Management System).
```
Input variables:
bms_serverurl, (required: True), Description: "URL of the BMS server."
bms_serverport, (required: False), Description: "Port of the BMS bConnect service, Defaults to: 443."
bms_CM_entry, (required: True), Description: "Name of the object in the credential manager."
bms_username, (required: True), Description: "Username to log into the BMS bconnect API."
bms_app_name, (required: True), Description: "Application name in BMS."
bms_app_vendor, (required: True), Description: "Application vendor name in BMS."
bms_app_parentid, (required: True), Description: "GUID of the Parent OU in BMS."
bms_app_version, (required: True), Description: "Application version in BMS."
bms_app_valid4os, (required: True), Description: "Valid OS for the application in BMS."
bms_app_seccont, (required: True), Description: "Application's security context in BMS."
bms_app_installcmd, (required: True), Description: "Application install command line in BMS."
bms_app_installbds, (required: False), Description: "BDS installscript path line in BMS."
bms_app_installparm, (required: False), Description: "Application install parameters in BMS."
bms_app_iopt_rebootbhv, (required: False), Description: "Application install option <reboot behaviour> in BMS."
bms_app_iopt_usebbt, (required: False), Description: "Application install option <support bbt> in BMS."
bms_app_iopt_copylocal, (required: False), Description: "Application install option <copy locally> in BMS."
bms_app_iopt_reinstall, (required: False), Description: "Application install option <Reinstallation allowed> in BMS."
bms_app_iopt_target, (required: False), Description: "Application install option <target> in BMS."
bms_app_comment, (required: False), Description: "Application comment in BMS."
bms_app_conschecks, (required: False), Description: "Application consistency check in BMS."
bms_app_uninstcmd, (required: False), Description: "Application uninstall command line in BMS."
bms_app_uninstbds, (required: False), Description: "BDS uninstall script path line in BMS."
bms_app_uninstparm, (required: False), Description: "Application uninstall parameters in BMS."
bms_app_uopt_rebootbhv, (required: False), Description: "Application uninstall option <reboot behaviour> in BMS."
bms_app_uopt_usebbt, (required: False), Description: "Application uninstall option <support bbt> in BMS."
bms_app_localfilecopy, (required: False), Description: "(Array of) 'Source~~~ObjectType' of (a) file or folder source(s). Use exactly 3 ~(tilde) as delimiter!"
bms_app_dependencies, (required: False), Description: "(Array of) 'Name~~~Version' of (a) dependenc(y/ies). Use exactly 3 ~(tilde) as delimiter!"
inst_file_src_dest, (required: False), Description: "Application install file(s) to copy to the DIP-Share, use wildcards for multiple objects."
read_file_src_dest, (required: False), Description: "Application readme and/or create-log file(s) to copy to the DIP-Share, use wildcards for multiple objects."
bms_imp_logfile, (required: False), Description: "Path to a logfile for exensive logging of the importer."
ignore_errors, (required: False), Description: "Ignore any errors during the run."
```

CharToNum
--------------
Calculate a number from a given string (a/A=1...z/Z=26) and return the number.
```
Input variables:
input_var, (required: True), Description: "string."
output_var, (required: True), Description: "string."
Output variables:
value of "output_var"
```

ChromiumSettings
--------------
Create a preference string for Chromium based browsers.
```
Input variables:
product_GUID, (required: False), Description: "The product GUID, if needed in the preferences."
new_settings, (required: True), Description: "Dict of setting(s) to add, required."
ignore_errors, (required: False), Description: "Ignore any errors during the process."
Output variables:
chrm_settings_url, Description: "Url-encoded string of settings."
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

ExecuteFile
-----------
Run an executable file (with arguments) (in a given directory).
```
Input variables:
exe_file, (required: True), Description: "Full path to the file to execute."
exe_folder, (required: False), Description: "Path to the dir, where the file should be executed."
cmdline_args, (required: False), Description: "(Array of) argument(s) to the command line."
run_elevated, (default: False, required: False), Description: "Run the EXE with elevated priviliges."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."
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
new_ver, (required: False), Description: "New version string to write."
re_pattern, (required: True), Description: "Regular expression of version string to replace."
```

FileMoverFromList
-----------------
Moves files from a source dir to a destination dir.
Filenames must bei provided by a listfile, line by line.
```
Input variables:
source_dir, (required: True), Description: "Path to the Source dir, relative to pkg_dir."
target_dir, (required: True), Description: "Path to the Target dir, relative to pkg_dir."
file_list, (required: True), Description: "Textfile containing the files to copy, line by line."
Output variables:
value of "file_list"
```

MozillaAddonIntegrator
----------------------
Install Extension(s) per computer and alter settings in the omni.ja in Mozilla products.
```
Input variables:
application_name, (required: True), Description: "Name of the the mozilla app (e.g. Firefox/Thunderbird."
install_exe, (required: True), Description: "Path to the exe of the mozilla app."
new_extensions, (required: True), Description: "(Array of) extension(s) to add, with name, full url to download and Wix-component-group separated by '|||'."
MakeFeatures, (default: False, required: False), Description: "Install the extension(s) as features."
omni_path, (default: "browser\\omni.ja", required: True), Description: "Internal Path to omni.ja in the exe file, relative."
config_file_path, (default: "chrome\\browser\\content\\browser\\built_in_addons.json", required: False), Description: "Internal Path to the config file to change in the omni.ja file, absolute."
temp_path, (required: False), Description: "Path to the folder where temporary files are stored, absolute."
omni_output_path, (required: False), Description: "Path to the folder where the altered omni file is stored, absolute."
ext_install_path, (required: True), Description: "Path to the folder where the extensions are stored, absolute."
app_build_path, (required: True), Description: "Path to the folder where the application build takes place, absolute."
ext_install_xslt, (required: False), Description: "Path to an XSLT file to transform Wix heat output, absolute."
ignore_errors, (required: False), Description: "Ignore any errors during the process."
```

MSBuildRun
----------
Run MSBuild to build a project.
```
Input variables:
build_file, (required: True), Description: "Buildfile to run in MSBuild."
build_folder, (required: True), Description: "Path to the build dir, required."
build_target, (required: False), Description: "Target to call in Buildfile."
build_property, {required: False), Description: "Property to set in Buildfile."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."
```

MSIAddFileHash
--------------
Get the hash of (a) file(s) and insert it into an MSI.
```
Input variables:
msi_path, (required: True), Description: "Path to the msi."
File2Hash, (required: True), Description: "(Array of) File(s) with key and full path to hash, separated by '|||'."
remove_version_field, (default: False, required: False), Description: "Clear the version field of the file in the MSI file table."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."
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
max_files_per_cab, (required: False), Description: "Optionally specify the maximum files per CAB."
embed_cab, (default: False, required: False), Description: "Embed the cabinet file in the MSI-file".
new_packcode, (default: False, required: False), Description: "Set a new packagecode in the MSI-file."
ignore_errors, (required: False), Description: "Ignore any errors during the run."
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
Deprecated! Use TextFileSearcher instead.
```
Input variables:
file_to_open, (required: True), Description: "The text file that needs to be opened for reading."
pattern, (required: True), Description: "The regex pattern to look for and return."
Output variables:
matchstring, Description: "Returns the string that matched the pattern."
```

TextFileSearcher
----------------
Loads a file and performs a regular expression match on the text.
```
Input variables:
file_to_open, (required: True), Description: "The text file that needs to be opened for reading."
re_pattern, (required: True), Description: "Regular expression (Python) to match against file."
result_output_var_name, (required: False, default: match), Description: "The name of the output variable that is returned by the match. If not specified then a default of 'match' will be used."
re_flags, (required: False), Description: "Optional array of strings of Python regular expression flags. E.g. IGNORECASE."
Output variables:
result_output_var_name, Description: "First matched sub-pattern from input found on the fetched file. Note the actual name of variable depends on the input variable 'result_output_var_name' or is assigned a default of 'match'."
```

WinPEVersionExtractor
---------------------
Extracts version info from Windows PE-executable (.exe/.dll) file.
```
Input variables:
exe_path, (required: False), Description: "Path to exe or msi, defaults to %pathname%."
product_version, (required: False), Description: "Set this flag to get the product version instead of the file version."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."
Output variables:
version, Description: "Version of exe found."
```

WixDarkExtractor
----------------
Extracts a resource from a Wix based exe using Dark.
```
Input variables:
exe_path, (required: False), Description: "Path to the (setup.)exe, defaults to %pathname%"
extract_dir, (required: True), Description: "Output path (absolute) for the extracted archive."
xtract_file, (required: False), Description: "Output filename of the resource to be extracted."
ignore_errors, (required: False), Description: "Ignore any errors during the extraction."
```

WixDefaults
-----------
Create version and default property files (version.wxi, global.prop) for the next NANT-(WIX-)build."
```
Input variables:
build_dir, (required: True), Description: "Path to the build_dir."
build_ver, (required: True), Description: "Version string, that we are using to build the package."
org_ver, (required: False), Description: "Original version string."
ignore_errors, (required: False), Description: "Ignore any errors during the run."
```