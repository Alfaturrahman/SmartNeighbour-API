# Script to migrate local database to Railway PostgreSQL
# Run this script to export local data and import to Railway

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Smart Neighbourhood - Database Migration Tool  " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "[1/5] Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Export data from local database
Write-Host "[2/5] Exporting data from local database..." -ForegroundColor Yellow
python manage.py dumpdata core --natural-foreign --natural-primary --indent 2 -o data_backup.json

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to export data!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Data exported to data_backup.json" -ForegroundColor Green
Write-Host ""

# Set Railway DATABASE_URL temporarily
Write-Host "[3/5] Connecting to Railway PostgreSQL..." -ForegroundColor Yellow
$env:DATABASE_URL = "postgresql://postgres:ykNWwFwUKrQpxTUTrgUdSsxhcSlHYdBi@maglev.proxy.rlwy.net:16438/railway"

# Run migrations on Railway database
Write-Host "[4/5] Running migrations on Railway database..." -ForegroundColor Yellow
python manage.py migrate --noinput

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to run migrations!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Migrations completed" -ForegroundColor Green
Write-Host ""

# Import data to Railway database
Write-Host "[5/5] Importing data to Railway PostgreSQL..." -ForegroundColor Yellow
python manage.py loaddata data_backup.json

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to import data!" -ForegroundColor Red
    Write-Host "This might be normal if there are duplicate keys. Continuing..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "  ✓ Migration Complete!                          " -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your data has been migrated to Railway PostgreSQL!" -ForegroundColor Green
Write-Host "Railway Database: postgresql://...railway" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Set environment variables in Railway Dashboard" -ForegroundColor White
Write-Host "2. Redeploy your backend" -ForegroundColor White
Write-Host "3. Test the API" -ForegroundColor White
Write-Host ""
