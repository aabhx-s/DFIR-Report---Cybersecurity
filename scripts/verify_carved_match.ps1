<#
.SYNOPSIS
    verify_carved_match.ps1 - Compares SHA-256 of Deleted Directory Entry vs PhotoRec Carved File.
#>

$ExportDir = Join-Path $PSScriptRoot "..\evidence\exported"
$DeletedFile = Join-Path $ExportDir "_XFIL_KEY.TXT"
$CarvedFile  = Join-Path $ExportDir "f0000000.txt"

Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host " RECOVERED FILE SHA-256 COMPARISON (DELETED vs. CARVED)" -ForegroundColor Cyan
Write-Host "==========================================================================" -ForegroundColor Cyan

if ((Test-Path $DeletedFile) -and (Test-Path $CarvedFile)) {
    $DeletedHash = (Get-FileHash -Path $DeletedFile -Algorithm SHA256).Hash
    $CarvedHash  = (Get-FileHash -Path $CarvedFile -Algorithm SHA256).Hash
    $DeletedSize = (Get-Item $DeletedFile).Length
    $CarvedSize  = (Get-Item $CarvedFile).Length

    Write-Host "Deleted File  : _XFIL_KEY.TXT"
    Write-Host "  Size        : $DeletedSize bytes"
    Write-Host "  SHA-256     : $DeletedHash" -ForegroundColor Yellow

    Write-Host "`nCarved File   : f0000000.txt"
    Write-Host "  Size        : $CarvedSize bytes"
    Write-Host "  SHA-256     : $CarvedHash" -ForegroundColor Yellow

    $Match = ($DeletedHash -eq $CarvedHash)
    if ($Match) {
        Write-Host "`nSHA-256 Comparison Result: True" -ForegroundColor Green
    } else {
        Write-Host "`nSHA-256 Comparison Result: False" -ForegroundColor Red
    }
} else {
    Write-Warning "Exported files not found. In Autopsy, right-click _XFIL_KEY.TXT and f0000000.txt -> Extract File."
}
