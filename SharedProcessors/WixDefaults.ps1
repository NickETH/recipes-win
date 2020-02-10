# Create version and default property files (version strings, GUID).
# PowerShell -NoProfile -ExecutionPolicy Bypass -Command "& '%cd%\WixDefaults.ps1'"
# 20190523, Nick Heim: Replace FFVersion with "RealVersion" (generalize...)

param(
    [Parameter(mandatory=$true)][string]$build_dir,
    [Parameter(mandatory=$true)][string]$build_ver,
    [Parameter(mandatory=$false)][string]$org_ver,
    [Parameter(mandatory=$false)][string]$prop_file
);

#Create a version string without delimiters
$CurrShortver= $build_ver -Replace ("\.", "")
echo ("Next Short Version: " + $CurrShortver)
cd ..

#Ugrade version consists of exactly 3 fields.
$UpgradeTest = $build_ver + ".0.0"
$UpgradeTest -match '(^\d+\.\d+\.\d+)'
$UpgradeVer = $Matches[0]

# version.wxi aktualisieren
$xml = [xml](Get-Content ($build_dir + "\wixproject\version.wxi"))
$NewGUID=[System.GUID]::NewGuid().ToString().ToUpper()

$defsnodes = $xml.SelectNodes("/Include/processing-instruction('define')")

foreach ($node in $defsnodes){
echo $node.value
switch ($node.Value)
{
    {$_ -match "Productcode="}
    {$node.Value = 'Productcode="{' + $NewGUID + '}"';BREAK}

    {$_.Substring(0,9) -match "version="}
    {$node.Value = 'version="' + $org_ver + '"';BREAK}

    {$_ -match "upgradeversion="}
    {$node.Value = 'upgradeversion="' + $UpgradeVer + '"';BREAK}

    {$_ -match "ETHZBuildNr="}
    {$node.Value = 'ETHZBuildNr="1"';BREAK}
}
echo $node.value
}
$xml.Save($build_dir + "\wixproject\version.wxi")

# PropFile aktualisieren
if ($prop_file -and $build_dir) {
    $xml = [xml](Get-Content ($build_dir + "\" + $prop_file))
    $propnodes = $xml.SelectNodes("/project/property")

    foreach ($node in $propnodes){
    echo $node.name
    switch ($node.name)
    {
        {$_ -match "download-component"}
        {$node.Value = "yes";BREAK}

        {$_ -match "RealVersion"}
        {$node.Value = $org_ver ;BREAK}

        {$_ -match "PackageVersion"}
        {$node.Value = $build_ver ;BREAK}

        {$_ -match "ShortVersion"}
        {$node.Value = $CurrShortver ;BREAK}

        {$_ -match "xpi-maxversion"}
        {$node.Value = $org_ver.Substring(0,2) + ".*" ;BREAK}

    }
    echo $node.value
    }
    $xml.Save($build_dir + "\" + $prop_file)
}
