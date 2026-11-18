<#
.SYNOPSIS
    verify_hashes.ps1 - Verifies evidence integrity and carved file matches.
#>

$EvidenceDir = Join-Path $PSScriptRoot "..\evidence"
$SourceImage = Join-Path $EvidenceDir "E002-vance-usb.dd"
$WorkingCopy = Join-Path $EvidenceDir "E002-vance-working.dd"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " DIGITAL EVIDENCE HASH INTEGRITY VERIFICATION (SHA-256)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

if ((Test-Path $SourceImage) -and (Test-Path $WorkingCopy)) {
    $SourceHash = (Get-FileHash -Path $SourceImage -Algorithm SHA256).Hash
    $WorkingHash = (Get-FileHash -Path $WorkingCopy -Algorithm SHA256).Hash

    Write-Host "Source Evidence Path : $SourceImage"
    Write-Host "Source SHA-256       : $SourceHash" -ForegroundColor Yellow
    Write-Host "Working Copy Path    : $WorkingCopy"
    Write-Host "Working SHA-256      : $WorkingHash" -ForegroundColor Yellow

    $Match = ($SourceHash -eq $WorkingHash)
    if ($Match) {
        Write-Host "`nIntegrity Check Match: True" -ForegroundColor Green
    } else {
        Write-Host "`nIntegrity Check Match: False" -ForegroundColor Red
    }
} else {
    Write-Warning "Evidence disk images not found. Run build_titan_evidence.py first."
}
