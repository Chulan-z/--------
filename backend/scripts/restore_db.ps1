param(
    [Parameter(Mandatory=$true)][string]$BackupFile,
    [string]$DatabaseUrl = $env:DATABASE_URL
)

if (-not $DatabaseUrl) {
    $DatabaseUrl = "postgresql://news:news@localhost:5432/newsdb"
}

pg_restore --clean --if-exists -d $DatabaseUrl $BackupFile
Write-Output "Database restored from: $BackupFile"
