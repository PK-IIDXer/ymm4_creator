# Stop script on error
$ErrorActionPreference = "Stop"

Write-Host "Starting code quality checks..." -ForegroundColor Cyan

# Format and lint code with Ruff
Write-Host "`nFormatting and linting code with Ruff..." -ForegroundColor Yellow
ruff format .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error occurred while running Ruff formatter" -ForegroundColor Red
    exit 1
}

ruff check . --fix
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error occurred while running Ruff linter" -ForegroundColor Red
    exit 1
}

Write-Host "`nAll checks completed!" -ForegroundColor Green 