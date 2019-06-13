# Create new GUID for Adobe Acrobat products, which contains the version as hex digits.
# PowerShell -NoProfile -ExecutionPolicy Bypass -Command "& '%cd%\WixDefaults.ps1'"

param(
    [Parameter(mandatory=$true)][string]$base_GUID,
    [Parameter(mandatory=$true)][string]$new_ver,
    [Parameter(mandatory=$true)][string]$old_hex_ver
);

    echo ("New GUID: " + $base_GUID)
# $AdbeRdrDC_baseGUID = "{AC76BA86-7AD7-1031-7B44-AC0F074E4100}"
#Split the version string into Major.Minor.build
$MajorVerStr,$MinorVerStr,$BuildVerStr = $new_ver.split('.',3)
$MajorVerHex = [String]::Format("{0:X2}", $MajorVerStr.TrimStart("0") -as [int])
$MinorVerHex = [String]::Format("{0:X2}", $MinorVerStr.TrimStart("0") -as [int])
$BuildVerHex = [String]::Format("{0:X4}", $BuildVerStr -as [int])
$newGUID = $base_GUID -replace $old_hex_ver, ($MajorVerHex + $MinorVerHex + $BuildVerHex)
    echo ("New GUID: " + $newGUID)
return "New GUID: " + $newGUID