#!/usr/bin/env pwsh
<#
.SYNOPSIS
Run SafeType+ Backend and Frontend
.DESCRIPTION
Starts backend on port 5000 and frontend on port 3000
#>

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "SafeType+ - Full Stack Runner" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$Info = "Cyan"
$Warning = "Yellow"
$Success = "Green"

# Start Backend in a new window
Write-Host "[1/2] Starting Backend (Flask)..." -ForegroundColor $Info
Write-Host "      Opening separate window for backend..." -ForegroundColor $Warning
Write-Host ""

$backendScript = @"
cd D:\pilot\safeType+\backend
.\.venv\Scripts\Activate.ps1
python app.py
"@

$backendPath = "D:\pilot\safeType+\backend_start.ps1"
$backendScript | Out-File -FilePath $backendPath -Encoding UTF8 -Force

# Start backend in new window
Start-Process powershell.exe -ArgumentList "-NoExit -File `"$backendPath`"" -WindowStyle Normal

Write-Host "Backend window opened!" -ForegroundColor $Success
Write-Host ""

# Wait for backend to start
Write-Host "Waiting 8 seconds for backend to initialize..." -ForegroundColor $Warning
Start-Sleep -Seconds 8
Write-Host ""

# Start Frontend
Write-Host "[2/2] Starting Frontend (React)..." -ForegroundColor $Info
Write-Host "      Location: D:\pilot\safeType+\frontend" -ForegroundColor $Info
Write-Host "      URL: http://localhost:3000" -ForegroundColor $Info
Write-Host ""

Set-Location "D:\pilot\safeType+\frontend"

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor $Warning
    npm install
    Write-Host ""
}

Write-Host "Starting React development server..." -ForegroundColor $Info
Write-Host "Press Ctrl+C to stop frontend (backend will keep running)" -ForegroundColor $Warning
Write-Host ""

npm start
