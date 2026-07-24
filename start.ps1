Write-Host "Starting TalentFlow-AI 2.0..." -ForegroundColor Cyan
Write-Host ""

$root = $PSScriptRoot

$pythonCmd = if (Test-Path "$root\venv\Scripts\python.exe") { "$root\venv\Scripts\python.exe" } else { "python" }

Write-Host "Starting Backend API on port 8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root'; & '$pythonCmd' -m uvicorn backend.app:create_app --factory --reload --port 8000"
Start-Sleep -Seconds 2

Write-Host "Starting Recruiter Dashboard on port 5173..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root/frontend/recruiter-dashboard'; npm run dev"
Start-Sleep -Seconds 2

Write-Host "Starting Candidate Portal on port 3001..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root/frontend/candidate-portal'; npm run dev"
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "All 3 services launched in separate terminal windows!" -ForegroundColor Green
Write-Host "  Backend API:          http://localhost:8000" -ForegroundColor Yellow
Write-Host "  API Docs:             http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "  Recruiter Dashboard:  http://localhost:5173" -ForegroundColor Yellow
Write-Host "  Candidate Portal:     http://localhost:3001" -ForegroundColor Yellow
Write-Host ""
