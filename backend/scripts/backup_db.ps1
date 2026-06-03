param(
    [string]$DatabaseUrl = $env:DATABASE_URL,
    [string]$BackupDir = "backups"
)

if (-not $DatabaseUrl) {
    $DatabaseUrl = "postgresql://news:news@localhost:5432/newsdb"
}

New-Item -ItemType Directory -Force $BackupDir | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$file = Join-Path $BackupDir "backup_$timestamp.dump"
pg_dump -Fc $DatabaseUrl -f $file
Write-Output "Backup created: $file"
