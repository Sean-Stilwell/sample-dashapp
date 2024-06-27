# Install the Az module (if not already installed)
# Az Module is required to interact with Azure Key Vault
# Install Az module if not already installed
if (-not (Get-Module -Name Az -ListAvailable)) {
    Install-Module -Name Az -AllowClobber -Scope CurrentUser
}
# Install the SecretManagement and SecretStore modules
# These modules are required to interact with the Secret Management module
# which will store the secrets locally. This avoids saving the secrets in a text file
if (-not (Get-Module -Name Microsoft.PowerShell.SecretStore -ListAvailable)) {
    Install-Module -Name Microsoft.PowerShell.SecretStore -AllowClobber -Scope CurrentUser
}
if (-not (Get-Module -Name Microsoft.PowerShell.SecretManagement -ListAvailable)) {
    Install-Module -Name Microsoft.PowerShell.SecretManagement -AllowClobber -Scope CurrentUser
}

# Connect to Azure if not already connected
$env:AzureTenantId = "8c1a4d93-d828-4d0e-9303-fd3bd611c822"
Connect-AzAccount -Tenant $env:AzureTenantId 

# Optional: Set the context to the specific Azure subscription
# Get-AzSubscription -SubscriptionName "Your Subscription Name" | Set-AzContext

# Define Key Vault URL or name
$KeyVaultName = "fsdh-proj-dw1-poc-kv"

Write-Output "Retrieving secrets from Key Vault: $KeyVaultName"
# Retrieve secrets from Key Vault
$DB_HOST = Get-AzKeyVaultSecret -VaultName $KeyVaultName -Name "datahub-psql-server" -AsPlainText
$DB_USER = Get-AzKeyVaultSecret -VaultName $KeyVaultName -Name "datahub-psql-admin" -AsPlainText
$DB_PASS = Get-AzKeyVaultSecret -VaultName $KeyVaultName -Name "datahub-psql-password" -AsPlainText
#Register-SecretVault -Name MyVault -ModuleName Microsoft.PowerShell.SecretStore -DefaultVault

# Output the secrets (optional, for verification)
Write-Output "Saving DB_HOST: $DB_HOST to Powershell Vault"
Set-Secret -Name DB_HOST -Secret $DB_HOST -Vault MyVault
Write-Output "Saving DB_USER: $DB_USER to Powershell Vault"
Set-Secret -Name DB_USER -Secret $DB_USER -Vault MyVault
Write-Output "Saving DB_PASS: $DB_PASS to Powershell Vault"
Set-Secret -Name DB_PASS -Secret $DB_PASS -Vault MyVault
