<#
.SYNOPSIS
    convert_timestamps.ps1 - Converts Chromium WebKit microsecond timestamps to Human-Readable CST/Local time.
#>

$ChromiumTimestamps = @(
    @{ Url = "https://search.internal/q=skyline+dynamics+headquarters+zurich"; Title = "Skyline Dynamics - Autonomous Systems HQ"; Microseconds = 13439264700000000 },
    @{ Url = "https://proton.me/drive/u/0/shared-folder-upload"; Title = "Proton Drive - Secure Encrypted Storage"; Microseconds = 13439265000000000 },
    @{ Url = "https://cyber-tools.net/sandisk-secure-wiper-utility"; Title = "SanDisk USB Clean Eraser & Slack Wiper"; Microseconds = 13439268300000000 },
    @{ Url = "https://ohare.airport/flights/departures/LX0019"; Title = "Flight LX-0019 Departure Status - Chicago O'Hare"; Microseconds = 13439268900000000 }
)

Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host " CHROMIUM WEBKIT TIMESTAMP CONVERSION (Case DF-2026-TITAN)" -ForegroundColor Cyan
Write-Host " Formula: [DateTime]::FromFileTimeUtc(Microseconds * 10)" -ForegroundColor Cyan
Write-Host "==========================================================================" -ForegroundColor Cyan

$results = foreach ($entry in $ChromiumTimestamps) {
    # Microseconds * 10 converts to 100-ns FileTime ticks
    $utcDate = [DateTime]::FromFileTimeUtc($entry.Microseconds * 10)
    # Convert UTC to CST (Central Standard Time: UTC - 6 hours)
    $cstDate = $utcDate.AddHours(-6)
    
    [PSCustomObject]@{
        "Timestamp (CST)" = $cstDate.ToString("yyyy-MM-dd HH:mm:ss")
        "Microseconds"    = $entry.Microseconds
        "Title"           = $entry.Title
        "URL"             = $entry.Url
    }
}

$results | Format-Table -AutoSize
