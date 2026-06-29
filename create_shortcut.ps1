#Requires -Version 5.1
<#
.SYNOPSIS
    Creates a Job Hunter shortcut that can be pinned to Start or the taskbar.
    Run once after cloning. Does not require admin rights.
    Monitored by CI -- any modification to this file triggers a review alert.
#>
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$AppDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$VbsFile = Join-Path $AppDir 'run.vbs'
$BatFile = Join-Path $AppDir 'run.bat'
$IcoFile = Join-Path $AppDir 'static\icon.ico'
$LnkFile = Join-Path $AppDir 'Job Hunter.lnk'

if (-not (Test-Path $BatFile)) {
    Write-Error "run.bat not found in $AppDir"
    exit 1
}
if (-not (Test-Path $VbsFile)) {
    Write-Error "run.vbs not found in $AppDir"
    exit 1
}
if (-not (Test-Path $IcoFile)) {
    Write-Error "Icon not found at $IcoFile -- run: python create_icons.py"
    exit 1
}

$Shell    = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($LnkFile)
$Shortcut.TargetPath       = "$env:SystemRoot\System32\wscript.exe"
$Shortcut.Arguments        = "`"$VbsFile`""
$Shortcut.WorkingDirectory = $AppDir
$Shortcut.Description      = 'Job Hunter - AI-powered job search assistant'
$Shortcut.IconLocation     = "$IcoFile,0"
$Shortcut.WindowStyle      = 1
$Shortcut.Save()

Write-Host ""
Write-Host "Shortcut created: $LnkFile"
Write-Host ""
Write-Host "  Pin to Start:   right-click Job Hunter.lnk -> Pin to Start"
Write-Host "  Pin to taskbar: right-click Job Hunter.lnk -> Show more options -> Pin to taskbar"
Write-Host ""
