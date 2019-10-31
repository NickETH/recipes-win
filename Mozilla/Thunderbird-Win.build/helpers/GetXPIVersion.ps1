param(
    [Parameter(mandatory=$true)][string]$infile,
    [Parameter(mandatory=$false)][string]$arg2,
    [Parameter(mandatory=$false)][string]$arg3
);

$infile = "manifest.json"

$json = Get-Content -Raw $infile | Out-String | ConvertFrom-Json

If ($json.applications.gecko.id){
    $ExtensionID = $json.applications.gecko.id
#    echo ("ID: " + $ExtensionID)
}
elseif ($json.browser_specific_settings.gecko.id){
    $ExtensionID = $json.browser_specific_settings.gecko.id
#    echo ("ID: " + $ExtensionID)
}
else{

    echo ("ExtensionID not found in " + $ExtensionID)
}

return $ExtensionID
