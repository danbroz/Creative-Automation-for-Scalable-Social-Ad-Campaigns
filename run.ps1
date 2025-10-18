# Creative Automation Pipeline Runner (PowerShell)
# Modern PowerShell script for Windows users

Write-Host "================================" -ForegroundColor Blue
Write-Host "Creative Automation Pipeline" -ForegroundColor Blue
Write-Host "================================`n" -ForegroundColor Blue

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Blue
& "venv\Scripts\Activate.ps1"

# Check if dependencies are installed
$null = python -c "import openai" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Dependencies not found. Installing..." -ForegroundColor Yellow
    pip install -q -r requirements.txt
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
}

# Check if brief file is provided
if ($args.Count -eq 0) {
    Write-Host "Usage: .\run.ps1 <brief_file.json> [--verbose]" -ForegroundColor Yellow
    Write-Host "`nExamples:"
    Write-Host "  .\run.ps1 examples\campaign_brief_1.json"
    Write-Host "  .\run.ps1 examples\campaign_brief_2.json --verbose"
    Write-Host "`nAvailable examples:"
    Write-Host "  - examples\campaign_brief_1.json (Wellness products)"
    Write-Host "  - examples\campaign_brief_2.json (Tech accessories)"
    Write-Host "  - examples\campaign_brief_3.json (Holiday gifts)"
    exit 1
}

# Run the pipeline
Write-Host "`nRunning pipeline...`n" -ForegroundColor Green
python -m src.main $args

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ Pipeline completed successfully!" -ForegroundColor Green
    Write-Host "Check the output\ directory for your generated assets." -ForegroundColor Blue
} else {
    Write-Host "`n⚠ Pipeline encountered errors. Check logs for details." -ForegroundColor Yellow
}

