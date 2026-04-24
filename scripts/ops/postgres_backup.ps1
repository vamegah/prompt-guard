param(
    [string]$OutputPath = "$(Get-Location)\backups",
    [string]$ContainerName = "promptguard-postgres",
    [string]$Database = "promptguard",
    [string]$User = "promptguard"
)

New-Item -ItemType Directory -Force -Path $OutputPath | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$file = Join-Path $OutputPath "promptguard-$timestamp.sql"

& "C:\Program Files\Docker\Docker\resources\bin\docker.exe" exec $ContainerName `
  pg_dump -U $User $Database > $file

Write-Output "Backup written to $file"
