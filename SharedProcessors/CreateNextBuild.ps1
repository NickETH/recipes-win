# Create next build directories and helper files in the build folder.
# Can normalize version fields (eg. Mozilla products).
# Can copy over files from a previous build (used eg in WIX builds to preserve component-GUIDS).
# V1.1: Introduce a version field in the "Build files" copy function.

# PowerShell -NoProfile -ExecutionPolicy Bypass -Command "& '%cd%\CreateNextBuild.ps1'"

param(
    [Parameter(mandatory=$true)][string]$build_dir,
    [Parameter(mandatory=$true)][string]$recipe_dir,
    [Parameter(mandatory=$true)][string]$org_ver,
    [Parameter(mandatory=$true)][string]$pkg_dir,
    [Parameter(mandatory=$true)][string]$folder_list,
    [Parameter(mandatory=$false)][string]$ver_fields,
    [Parameter(mandatory=$false)][string]$AS_ver,
    [Parameter(mandatory=$false)][string]$recipe_path,
    [Parameter(mandatory=$false)][string]$BuildFiles,
    [Parameter(mandatory=$false)][string]$recipe_cache_dir,
    [Parameter(mandatory=$false)][string]$PrevVerFiles
);

$fldr_seprtr = "|",":"
$split_optn = [System.StringSplitOptions]::RemoveEmptyEntries
$folder_ary = $folder_list.Split($fldr_seprtr,$split_optn)

If ($ver_fields){
	$VerArray = $org_ver.Split(".")
	$VerArray = $VerArray + @('0','0','0','0')
	$build_ver = $VerArray[0] 

    for ($i=1; $i -lt $ver_fields; $i++) {
		$build_ver = $build_ver + "." + $VerArray[$i]
	    echo ("build_ver: " + $build_ver)
    }
}
else{
    $build_ver = $org_ver
}
# echo ("ver_fields: " + $ver_fields)

<#$Ver_Regex = "^\d+"
If ($ver_fields){
	$ver_fields = $ver_fields - 1
    for ($i=1; $i -le $ver_fields; $i++) {
		$Ver_Regex = $Ver_Regex + "\.\d+"
	    echo ("Regex: " + $Ver_Regex)
    }
	$Ver_Regex_long = $Ver_Regex + "\.\d+"
	
    If ($org_ver -Match $Ver_Regex_long){
        echo ("Next Version1: " + $Matches[0])
        $build_ver = $org_ver
        echo ("Next Version2: " + $build_ver + " " + $Org_Version)
    }
    ElseIf ($org_ver -Match $Ver_Regex){
        echo ("Next Version3: " + $Matches[0])
        $build_ver = $org_ver + ".0"
        echo ("Next Version4: " + $build_ver + " " + $Org_Version)
	}
}
else{
    $build_ver = $org_ver
}
#>
$Return_string = "Buildversion: " + $build_ver

If ($AS_ver){
    $version_obj = $build_ver.Split(".")
    If ($version_obj.Length -le 3){
        $AS_versionstring = $build_ver.Replace(".",",")
    }
    ElseIf ($version_obj.Length -eq 4){
        $digit_Three = [int]$($version_obj[2] + $version_obj[3])
        If ($digit_Three -gt 65535){
            $digit_Three = [int]$($version_obj[2] + $version_obj[3]).Substring(0,4)
        }
        $AS_versionstring = $version_obj[0] + "," + $version_obj[1] + "," + $digit_Three.ToString()
    }
    $Return_string = $Return_string + " | ASversion: " + $AS_versionstring
}

#Save the pkg_dir template for previous build_dir
$prev_pkg_dir = $pkg_dir
#echo ("pkg_dir 1: " + $pkg_dir)
if ($pkg_dir -match "::VVeerrssiioonn::") {
    $pkg_dir = $pkg_dir.replace("::VVeerrssiioonn::", $build_ver)
}
#echo ("pkg_dirs 2: " + $pkg_dir)

if ($build_dir | Test-Path) {
    cd $build_dir
    if (-not ($pkg_dir | Test-Path)) {
        md $pkg_dir
    }
}

cd $pkg_dir
foreach ($folder in $folder_ary) {
    #echo ("Create-Folder-Foreach: " + $folder)
    if (-not ($folder | Test-Path)) {
        md $folder

    }
}

if ($BuildFiles -and $recipe_path) {
    foreach ($line in Get-Content ($BuildFiles)) {
        #echo ("BuildFiles-Foreach: " + ($recipe_path + "\" + $line))
        #echo ("BuildFiles-Foreach: " + $build_dir + "\" + $pkg_dir + "\" + $line)
        if ($line -match 'VVeerrssiioonn') {
            $line_build = $line.replace("VVeerrssiioonn", $build_ver)
        }
        else{
            $line_build = $line
        }
        if ($line -match '\*') {
            Copy-Item -Force -Recurse ($recipe_path + "\" + $line) ($build_dir + "\" + $pkg_dir + "\" + $line.Substring(0, $line.IndexOf("*")))
			#echo ("BuildFiles-Foreach: " + $build_dir + "\" + $pkg_dir + "\" + $line.Substring(0, $line.IndexOf("*")))
        }
        else{
            Copy-Item -Force ($recipe_path + "\" + $line) ($build_dir + "\" + $pkg_dir + "\" + $line_build)
			#echo ("BuildFiles-Foreach: " + $build_dir + "\" + $pkg_dir + "\" + $line)
        }
    }
}

if ($PrevVerFiles -and $recipe_cache_dir) {
    $prev_build_ver = Get-Content ($recipe_cache_dir + "\prev_version.txt").Trim()
	echo ("prev_build_ver 1: " + $prev_build_ver)
    if ($prev_pkg_dir -match "::VVeerrssiioonn::") {
        $prev_pkg_dir = $prev_pkg_dir.replace("::VVeerrssiioonn::", $prev_build_ver)
    }
    foreach ($line in Get-Content ($PrevVerFiles)) {
        echo ("PrevVerFiles-Foreach: " + $line)
        Copy-Item -Force ($build_dir + "\" + $prev_pkg_dir + "\wixproject\" + $line) ($build_dir + "\" + $pkg_dir + "\wixproject\Prev_Ver_" + $line)
    }
}
return $Return_string
