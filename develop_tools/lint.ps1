# Stop script on error
$ErrorActionPreference = "Stop"

Write-Host "Starting code quality checks..." -ForegroundColor Cyan

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

# Check code quality with Flake8
Write-Host "`nChecking code quality with Flake8..." -ForegroundColor Yellow
flake8 .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error occurred while running Flake8" -ForegroundColor Red
    exit 1
}

# Run type checking with mypy
Write-Host "`nRunning type checking with mypy..." -ForegroundColor Yellow
mypy .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error occurred while running mypy" -ForegroundColor Red
    exit 1
}

Write-Host "`nAll checks completed!" -ForegroundColor Green 