Param()

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $root "backend"
$frontendDir = Join-Path $root "frontend"
$pythonExe = Join-Path $root "venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
  Write-Host "Python venv not found at $pythonExe" -ForegroundColor Red
  exit 1
}

if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
  Write-Host "Installing frontend dependencies..."
  Push-Location $frontendDir
  npm install
  Pop-Location
}

Write-Host "Starting backend at http://localhost:8000 ..."
Start-Process -FilePath "powershell.exe" -WorkingDirectory $backendDir -ArgumentList @(
  "-NoExit",
  "-Command",
  "& `"$pythonExe`" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
)

Write-Host "Starting frontend at http://localhost:3000 ..."
Start-Process -FilePath "powershell.exe" -WorkingDirectory $frontendDir -ArgumentList @(
  "-NoExit",
  "-Command",
  "npm run dev"
)

Start-Sleep -Seconds 4
Start-Process "http://localhost:3000"
Write-Host "App launched in browser."

