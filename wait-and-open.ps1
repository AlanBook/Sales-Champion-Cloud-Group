$backendReady = $false
$frontendReady = $false
$deadline = (Get-Date).AddMinutes(5)

Write-Host "[INFO] Waiting for backend and frontend to become ready..."

while ((Get-Date) -lt $deadline) {
  try {
    $backend = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/healthz" -TimeoutSec 5
    if ($backend.StatusCode -eq 200) {
      $backendReady = $true
    }
  } catch {}

  try {
    $frontend = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:3000/login" -TimeoutSec 5
    if ($frontend.StatusCode -eq 200) {
      $frontendReady = $true
    }
  } catch {}

  if ($backendReady -and $frontendReady) {
    break
  }

  Start-Sleep -Seconds 5
}

if (-not ($backendReady -and $frontendReady)) {
  Write-Host "[ERROR] Service startup timed out."
  Write-Host "You can inspect logs with: docker compose logs"
  Read-Host "Press Enter to close"
  exit 1
}

Write-Host ""
Write-Host "Sales Champion Demo is ready."
Write-Host "Open URL: http://127.0.0.1:3000/login"
Write-Host "Demo accounts:"
Write-Host "  boss_demo / password"
Write-Host "  manager_demo / password"
Write-Host "  admin_demo / password"
Write-Host "  staff_08 / password"
Start-Process "http://127.0.0.1:3000/login"
