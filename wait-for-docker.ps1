$deadline = (Get-Date).AddMinutes(3)

while ((Get-Date) -lt $deadline) {
  docker info *> $null
  if ($LASTEXITCODE -eq 0) {
    exit 0
  }
  Start-Sleep -Seconds 5
}

exit 1
