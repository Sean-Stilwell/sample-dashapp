#!/usr/bin/env pwsh

if (-not (Get-Module -Name Microsoft.PowerShell.SecretManagement -ListAvailable)) {
    Install-Module -Name Microsoft.PowerShell.SecretManagement -AllowClobber -Scope CurrentUser
}
# loads the secrets into environment variables so that they can be accessed 
$env:DATAHUB_PSQL_SERVER = Get-Secret -Name DB_HOST -AsPlainText
$env:DATAHUB_PSQL_USER = Get-Secret -Name DB_USER -AsPlainText
$env:DATAHUB_PSQL_PASSWORD = Get-Secret -Name DB_PASS -AsPlainText

Write-Host "Configured environment variables from local vault"
