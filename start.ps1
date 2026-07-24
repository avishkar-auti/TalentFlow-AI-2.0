# TalentFlow-AI 2.0 - Start All Services (PowerShell)
# Usage: .\start.ps1

Write-Host "🚀 Starting TalentFlow-AI 2.0..." -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Function to start a service in a new window
function Start-Service {
    param(
        [string]$Name,
        [string]$Command,
        [string]$Port
    )

    Write-Host "📍 Starting $Name on port $Port..." -ForegroundColor Green

    $scriptBlock = {
        param($cmd, $dir)
        Set-Location $dir
        Invoke-Expression $cmd
    }

    Start-Process powershell -ArgumentList "-NoExit", "-Command", `
        "`$scriptBlock = {$scriptBlock}; & `$scriptBlock -cmd '$Command' -dir '$rootDir'"

    Start-Sleep -Milliseconds 500
}

# Start Backend
Start-Service -Name "Backend API" -Command "cd backend; python -m uvicorn app:app --reload --port 8000" -Port 8000

# Start Recruiter Dashboard
Start-Service -Name "Recruiter Dashboard" -Command "cd frontend/recruiter-dashboard; npm run dev" -Port 5173

# Start Candidate Portal
Start-Service -Name "Candidate Portal" -Command "cd frontend/candidate-portal; npm run dev" -Port 3001

Write-Host ""
Write-Host "✅ All services started!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 URLs:" -ForegroundColor Cyan
Write-Host "  Backend API:          http://localhost:8000" -ForegroundColor Yellow
Write-Host "  API Docs:             http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "  Recruiter Dashboard:  http://localhost:3001" -ForegroundColor Yellow
Write-Host "  Candidate Portal:     http://localhost:5173" -ForegroundColor Yellow
Write-Host ""
Write-Host "💡 Tip: Close individual terminal windows to stop each service" -ForegroundColor Cyan
Write-Host ""
