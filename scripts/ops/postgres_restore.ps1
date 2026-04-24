param(
    [Parameter(Mandatory=$true)][string]$BackupFile,
    [string]$ContainerName = "promptguard-postgres",
    [string]$Database = "promptguard",
    [string]$User = "promptguard"
)

if (-not (Test-Path $BackupFile)) {
    throw "Backup file not found: $BackupFile"
}

Get-Content $BackupFile | & "C:\Program Files\Docker\Docker\resources\bin\docker.exe" exec -i $ContainerName `
  psql -U $User $Database

Write-Output "Restore completed from $BackupFile"
