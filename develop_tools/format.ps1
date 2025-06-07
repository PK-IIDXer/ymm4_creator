# Stop script on error
$ErrorActionPreference = "Stop"

Write-Host "Starting code formatting..." -ForegroundColor Cyan

# Format code with Black
Write-Host "`nFormatting code with Black..." -ForegroundColor Yellow
black .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error occurred while running Black" -ForegroundColor Red
    exit 1
}

# Sort imports with isort
Write-Host "`nSorting imports..." -ForegroundColor Yellow
isort .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error occurred while running isort" -ForegroundColor Red
    exit 1
}

Write-Host "`nFormatting completed!" -ForegroundColor Green 