# Start SewaCircle locally on Windows: backend (offline replay mode) on :8000 and the website on :5173.
# Usage (from the repo root):  powershell -ExecutionPolicy Bypass -File .\start.ps1 [-ApiPort 8010]
# Use -ApiPort when port 8000 is already taken (Docker often uses it).
param([int]$ApiPort = 8000)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
if (-not (Test-Path "$root\.venv\Scripts\python.exe")) {
  Write-Host 'Creating Python environment (first run only)...'
  python -m venv "$root\.venv"
  & "$root\.venv\Scripts\python.exe" -m pip install -r "$root\backend\requirements.txt"
}
if (-not (Test-Path "$root\frontend\node_modules")) { Push-Location "$root\frontend"; npm ci; Pop-Location }
$env:SEWA_LLM_MODE = 'replay'
Start-Process -FilePath "$root\.venv\Scripts\python.exe" -ArgumentList '-m','uvicorn','app.main:app','--port',"$ApiPort" -WorkingDirectory "$root\backend"
Write-Host "Backend starting on http://127.0.0.1:$ApiPort ..."
$env:SEWA_API_PORT = "$ApiPort"
Push-Location "$root\frontend"; npm run dev; Pop-Location
