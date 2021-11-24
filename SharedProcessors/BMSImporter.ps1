# Create a new BMS Application

# PowerShell -NoProfile -ExecutionPolicy Bypass -Command "& '%cd%\BMSImporter.ps1'"
# Todo: Logfile based on the presence of a bms_imp_logfile parameter, better parameter read function(s).
# Extended with UseBBT-option and explicit options for uninstall, 20210207, Hm
# Extended localfilecopy to all options, 20211028, Hm

param(
    [Parameter(mandatory=$true)][string]$bms_serverurl,
    [Parameter(mandatory=$true)][string]$bms_serverport,
    [Parameter(mandatory=$true)][string]$bms_CM_entry,
    [Parameter(mandatory=$true)][string]$bms_username,
    [Parameter(mandatory=$true)][string]$bms_app_name,
    [Parameter(mandatory=$true)][string]$bms_app_vendor,
    [Parameter(mandatory=$true)][string]$bms_app_parentid,
    [Parameter(mandatory=$true)][string]$bms_app_version,
    [Parameter(mandatory=$true)][string]$bms_app_valid4os,
    [Parameter(mandatory=$true)][string]$bms_app_seccont,
    [Parameter(mandatory=$false)][string]$bms_app_installcmd,
    [Parameter(mandatory=$false)][string]$bms_app_installbds,
	[Parameter(mandatory=$false)][string]$bms_app_installparm,
    [Parameter(mandatory=$false)][string]$bms_app_iopt_rebootbhv,
    [Parameter(mandatory=$false)][string]$bms_app_iopt_copylocal,
    [Parameter(mandatory=$false)][string]$bms_app_iopt_usebbt,
    [Parameter(mandatory=$false)][string]$bms_app_iopt_reinstall,
    [Parameter(mandatory=$false)][string]$bms_app_iopt_target,
    [Parameter(mandatory=$false)][string]$bms_app_comment,
    [Parameter(mandatory=$false)][string]$bms_app_category,
    [Parameter(mandatory=$false)][string]$bms_app_conschecks,
    [Parameter(mandatory=$false)][string]$bms_app_uninstcmd,
	[Parameter(mandatory=$false)][string]$bms_app_uninstbds,
    [Parameter(mandatory=$false)][string]$bms_app_uninstparm,
    [Parameter(mandatory=$false)][string]$bms_app_uopt_rebootbhv,
    [Parameter(mandatory=$false)][string]$bms_app_uopt_usebbt,
	[Parameter(mandatory=$false)][string]$bms_app_localfilecopy,
    [Parameter(mandatory=$false)][string]$bms_app_dependencies,
    [Parameter(mandatory=$false)][string]$inst_file_src_dest,
    [Parameter(mandatory=$false)][string]$read_file_src_dest,
    [Parameter(mandatory=$false)][string]$bms_imp_logfile
);

$logfile = ("C:\Tools\AutoPKG\log\BMSimporter" + $bms_app_name + (Get-Date -Format yyyyMMdd-HHmm) + ".txt")

echo "----------Start of BMSimporter--------------" | Out-File $logfile -Append
echo ("bms_server: " + $bms_serverurl + " bms_appname: " + $bms_app_name) | Out-File $logfile -Append
# Convert a boolean string to a bool type value.
function ParseBool{
    [CmdletBinding()]
    param(
        [Parameter(Position=0)]
        [System.String]$inputVal
    )
    switch -regex ($inputVal.Trim())
    {
        "^(1|true|yes|on|enabled)$" { $true }

        default { $false }
    }
}
Import-Module bConnect
# Do we need to load this assemblies?
[Windows.Security.Credentials.PasswordVault,Windows.Security.Credentials,ContentType=WindowsRuntime]
$vault = New-Object Windows.Security.Credentials.PasswordVault

#Allow the usage of different encryption methods.
#https://stackoverflow.com/questions/11696944/powershell-v3-invoke-webrequest-https-error
$AllProtocols = [System.Net.SecurityProtocolType]'Ssl3,Tls,Tls11,Tls12'
[System.Net.ServicePointManager]::SecurityProtocol = $AllProtocols

#$bms_CM_entry = "AutoPKG-BMSImporter"
if (-Not ($storedCredential = $vault.Retrieve($bms_CM_entry, $bms_username))){
    $objCred = Get-Credential -UserName $bms_username -Message "Authentifizierung am Baramundi-Server:"
    # Convert credential to appropriate type and store in vault
    $credObject = New-Object Windows.Security.Credentials.PasswordCredential -ArgumentList ($bms_CM_entry, $objCred.UserName,$objCred.GetNetworkCredential().Password)
    $vault.Add($credObject)
}

# Retrieve the credential from vault
$storedCredential = $vault.Retrieve($bms_CM_entry, $bms_username)
# Create a PSCredential object to give to bConnect
$objCred = New-Object System.Management.Automation.PSCredential -ArgumentList ($storedCredential.UserName, (ConvertTo-SecureString $storedCredential.Password -AsPlainText -Force))

Initialize-bConnect -Server $bms_serverurl -Port $bms_serverport -Credentials $objCred
<#
echo "InstallOptions" | Out-File $logfile -Append
echo "bms_app_iopt_copylocal: " + $bms_app_iopt_copylocal | Out-File $logfile -Append
echo "bms_app_iopt_rebootbhv: " + $bms_app_iopt_rebootbhv | Out-File $logfile -Append
#>

# Check for an existing application with the same name and version.
# If an application with same name and version exists in the staging OU, we will remove it.
# If an application with same name and version exists in another OU, we can not alter it and have to stop here.
# We are searching trough all the applications on this server! Eye on perfomance! Alternative: a parameter array with the OU's to search...
# $All_Apps_in_OU = Get-bConnectApplication -OrgUnitGuid $bms_app_parentid
$All_Apps_in_BMS = Get-bConnectApplication
foreach ($Application in $All_Apps_in_BMS) {
    if ($Application.Name -eq $bms_app_name -and $Application.Version -eq $bms_app_version -and $Application.ParentId -eq $bms_app_parentid){
        Remove-bConnectApplication -ApplicationGuid $Application.Id
        echo "An application with the same name and version was removed from the staging OU!" | Out-File $logfile -Append
    }
    Elseif ($Application.Name -eq $bms_app_name -and $Application.Version -eq $bms_app_version -and $Application.ParentId -ne $bms_app_parentid){
        echo "An application with the same name and version is already in production!" | Out-File $logfile -Append
        Exit
        #[Environment]::Exit(0)
    }
}

# Create the options hash table for install
if ($bms_app_iopt_rebootbhv -or $bms_app_iopt_copylocal -or $bms_app_iopt_usebbt -or $bms_app_iopt_reinstall -or $bms_app_target) {
    $InstallOptArgs = @{ }
    # echo "InstallOptions inside If" | Out-File $logfile -Append
    # echo ("bms_app_iopt_copylocal in If: " + $bms_app_iopt_copylocal) | Out-File $logfile -Append

    # echo @InstallOptArgs | Out-File $logfile -Append
    if ($bms_app_iopt_rebootbhv) { $InstallOptArgs['RebootBehaviour'] = $bms_app_iopt_rebootbhv}
    if ($bms_app_iopt_copylocal ) { $InstallOptArgs['CopyLocally'] = (ParseBool($bms_app_iopt_copylocal)) }
    if ($bms_app_iopt_usebbt ) { $InstallOptArgs['UsebBT'] = (ParseBool($bms_app_iopt_usebbt)) }
    if ($bms_app_iopt_reinstall ) { $InstallOptArgs['AllowReinstall'] = (ParseBool($bms_app_iopt_reinstall)) }
    if ($bms_app_iopt_target) { $InstallOptArgs['Target'] = $bms_app_iopt_target }
    # echo @InstallOptArgs | Out-File $logfile -Append
    $InstallOptions = New-bConnectApplicationInstallOptions @InstallOptArgs
    # echo @InstallOptArgs | Out-File $logfile -Append
    # echo "1" | Out-File $logfile -Append
}
# Create the options hash table for uninstall
# Special case for reboot behaviour: If it is set on install, we use it also for uninstall as default. But if it set for uninstall explicitley, we take this one.
if ($bms_app_iopt_rebootbhv -or $bms_app_uopt_rebootbhv -or $bms_app_uopt_usebbt) {
	$UnInstallOptArgs = @{ }
	if ($bms_app_iopt_rebootbhv) { $UnInstallOptArgs['RebootBehaviour'] = $bms_app_iopt_rebootbhv}
	if ($bms_app_uopt_rebootbhv) { $UnInstallOptArgs['RebootBehaviour'] = $bms_app_uopt_rebootbhv}
	if ($bms_app_uopt_usebbt) { $UnInstallOptArgs['UsebBT'] = (ParseBool($bms_app_uopt_usebbt)) }
	$UnInstallOptions = New-bConnectApplicationInstallOptions @UnInstallOptArgs
}

if ($bms_app_installbds -and $bms_app_installcmd) {
	$installDataArgs = @{
		Command	   = $bms_app_installcmd;
		EngineFile	   = $bms_app_installbds;
	}
}
elseif ($bms_app_installcmd) {
	$installDataArgs = @{
		Command	   = $bms_app_installcmd;
	}
}
elseif ($bms_app_installbds) {
	$installDataArgs = @{
		EngineFile	   = $bms_app_installbds;
	}
}

if ($bms_app_installparm) { $installDataArgs['Parameter'] = $bms_app_installparm }
if ($InstallOptions) { $installDataArgs['Options'] = $InstallOptions }
$InstallationData = New-bConnectApplicationInstallationData @installDataArgs
# echo @InstallationData | Out-File $logfile -Append
# echo "2" | Out-File $logfile -Append

if ($bms_app_uninstcmd -or $bms_app_uninstbds -or $bms_app_uninstparm) {
	if ($bms_app_uninstcmd -and $bms_app_uninstbds) {
		$UnInstallDataArgs = @{
			Command = $bms_app_uninstcmd;
			EngineFile = $bms_app_uninstbds;
		}
	}
	elseif ($bms_app_uninstcmd) {
		$UnInstallDataArgs = @{
			Command	= $bms_app_uninstcmd;
		}
	}
	elseif ($bms_app_uninstbds) {
		$UnInstallDataArgs = @{
			EngineFile = $bms_app_uninstbds;
		}
	}
    if ($bms_app_uninstparm) { $UnInstallDataArgs['Parameter'] = $bms_app_uninstparm }
	if ($UnInstallOptions) { $UnInstallDataArgs['Options'] = $UnInstallOptions }
    $UninstallationData = New-bConnectApplicationInstallationData @UnInstallDataArgs
    # echo @UninstallationData | Out-File $logfile -Append
    # echo "3" | Out-File $logfile -Append
}


#Create an array for the "ValidForOS" object.
$Val4OSary = $bms_app_valid4os.Split(",") | where-object {$_ -ne " "}

# echo ("Valid4OS-before: " + $bms_app_valid4os) | Out-File $logfile -Append
# echo ("Valid4OS-after: " + $Val4OSary) | Out-File $logfile -Append

$AppInstallArgs = @{
    Name             = $bms_app_name;
    Vendor           = $bms_app_vendor;
    Version          = $bms_app_version;
    ValidForOS       = $Val4OSary;
    ParentId         = $bms_app_parentid;
    SecurityContext  = $bms_app_seccont;
    InstallationData = $InstallationData;
}

#A bunch of optional settings
if ($bms_app_category) { $AppInstallArgs['Category'] = $bms_app_category }
if ($bms_app_comment) { $AppInstallArgs['Comment'] = $bms_app_comment }
if ($UninstallationData) { $AppInstallArgs['UninstallationData'] = $UninstallationData }
if ($bms_app_conschecks) { $AppInstallArgs['ConsistencyChecks'] = $bms_app_conschecks }

#If we have to config files to copy locally
if ($bms_app_localfilecopy) {
    $fldr_seprtr = "|||"
    $split_optn = [System.StringSplitOptions]::RemoveEmptyEntries
    $local_file_ary = $bms_app_localfilecopy.Split($fldr_seprtr,$split_optn)
    $App_LocalFile_Arj = @()
    $fldr_seprtr = "~~~"
    foreach ($local_file in $local_file_ary) {
        $local_file_opt = $local_file.Split($fldr_seprtr,$split_optn)
		$File_obj_local = New-bConnectApplicationFile -Source $local_file_opt[0] -Type $local_file_opt[1]
		$App_localFile_Arj += @( [PSCustomObject]$File_obj_local)
    }
	if ($File_obj_local) { $AppInstallArgs['Files'] = $App_localFile_Arj }
	
	# echo ("Local File: " + $bms_app_localfilecopy) | Out-File $logfile -Append
}

#If we have dependencies
if ($bms_app_dependencies) {
    $fldr_seprtr = "|||"
    $split_optn = [System.StringSplitOptions]::RemoveEmptyEntries
    $depend_file_ary = $bms_app_dependencies.Split($fldr_seprtr,$split_optn)
    $App_Depend_Arj = @()
    $fldr_seprtr = "~~~"
    foreach ($depend_file in $depend_file_ary) {
        $depend_file_opt = $depend_file.Split($fldr_seprtr,$split_optn)

        foreach ($Application in $All_Apps_in_BMS) {
            if ($Application.Name -eq $depend_file_opt[0] -and $Application.Version -eq $depend_file_opt[1]){
                $App_Dep = @{
                    DependencyId      = $Application.Id;
                    DependencyAppName = $Application.Name;
                    DependencyType    = [PSCustomObject]"InstallBeforeIfNotInstalled";
                    ValidForOS        = [PSCustomObject]$Val4OSary
                }
    			$Depend_Data = New-bConnectApplicationDependency @App_Dep
                $App_Depend_Arj += @( [PSCustomObject]$Depend_Data)
            }
        }
        # echo ("Dependency " + $Application.Name) | Out-File $logfile -Append
    }
    $AppInstallArgs['SoftwareDependencies'] = $App_Depend_Arj
}

# echo @AppInstallArgs | Out-File $logfile -Append
# echo "Just before New-App" | Out-File $logfile -Append
<#
#>
# echo @AppInstallArgs | Out-File $logfile -Append

New-bConnectApplication @AppInstallArgs

#Copy the install file(s) to the destination storage location
if ($inst_file_src_dest) {
    $fldr_seprtr = "|"
    $split_optn = [System.StringSplitOptions]::RemoveEmptyEntries
    $inst_file_ary = $inst_file_src_dest.Split($fldr_seprtr,$split_optn)
    if( -Not (Test-Path -Path $inst_file_ary[1])){
        New-Item -Type dir $inst_file_ary[1]
    }
    # echo ("inst_file_src_dest: " + ($inst_file_ary[0] + "  " + $inst_file_ary[1]))
    if ($inst_file_ary[0] -match '\*') {
        Copy-Item -Force -Recurse $inst_file_ary[0] $inst_file_ary[1]
    }
    else{
        Copy-Item -Force $inst_file_ary[0] $inst_file_ary[1]
    }
}

#Copy the readme/create-log file(s) to the destination storage location
if ($read_file_src_dest) {
    $fldr_seprtr = "|"
    $split_optn = [System.StringSplitOptions]::RemoveEmptyEntries
    $read_file_ary = $read_file_src_dest.Split($fldr_seprtr,$split_optn)
    if( -Not (Test-Path -Path $read_file_ary[1])){
        New-Item -Type dir $read_file_ary[1]
    }
    # echo ("read_file_src_dest: " + ($read_file_ary[0] + "  " + $read_file_ary[1]))
    if ($read_file_ary[0] -match '\*') {
        Copy-Item -Force -Recurse $read_file_ary[0] $read_file_ary[1]
    }
    else{
        Copy-Item -Force $read_file_ary[0] $read_file_ary[1]
    }

}
echo ("----------End of BMSimporter -- bms_server: " + $bms_serverurl + " bms_appname: " + $bms_app_name + " --------------")| Out-File $logfile -Append

