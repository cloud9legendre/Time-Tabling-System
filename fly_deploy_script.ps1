# Fly.io Deployment Script
# Usage: .\fly_deploy_script.ps1

Write-Host "Starting Fly.io Deployment Setup..."

# 1. Check for flyctl
if (!(Get-Command "flyctl" -ErrorAction SilentlyContinue)) {
    Write-Error "flyctl not found. Please ensure it is in your PATH."
    exit 1
}

# 2. Create Database
Write-Host "Creating Postgres Database (clts-db-prod)..."
# Note: Using 'lhr' (London) as it is widely available. Change to 'maa' if available after billing setup.
flyctl postgres create --name clts-db-prod --region lhr --initial-cluster-size 1 --vm-size shared-cpu-1x --volume-size 1 --org personal

if ($LASTEXITCODE -ne 0) {
    Write-Error "Database creation failed. Please check your Fly.io billing status."
    exit $LASTEXITCODE
}

# 3. Initialize App
Write-Host "Initializing Backend App..."
Set-Location "backend" 

# Generate a unique app name
$AppName = "clts-backend-" + -join ((65..90) + (97..122) | Get-Random -Count 5 | % {[char]$_})
Write-Host "App Name: $AppName"

# Launch config (creates fly.toml) but does not deploy yet
flyctl launch --no-deploy --copy-config --name $AppName --region lhr --org personal --postgres-app clts-db-prod

# 4. Set Secrets
Write-Host "Setting Secrets..."
# specific secret key - in prod, generate a real one
flyctl secrets set SECRET_KEY="super-secure-secret-key-change-me" ACCESS_TOKEN_EXPIRE_MINUTES=60

# 5. Deploy
Write-Host "Deploying..."
flyctl deploy

Write-Host "Deployment Complete! Check the URL above."
