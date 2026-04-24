param(
  [switch]$Keep
)

$composeArgs = @("compose", "-f", "backend/docker-compose.prod.yml")

function Invoke-Compose {
  param([string[]]$Args)
  & docker @Args
  if ($LASTEXITCODE -ne 0) {
    throw "Docker compose failed: $Args"
  }
}

function Wait-ForHttp {
  param(
    [string]$Url,
    [int]$Retries = 30,
    [int]$DelaySeconds = 2
  )
  for ($i = 0; $i -lt $Retries; $i++) {
    try {
      $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
      if ($resp.StatusCode -eq 200) {
        return
      }
    } catch {
      Start-Sleep -Seconds $DelaySeconds
    }
  }
  throw "Timed out waiting for $Url"
}

Invoke-Compose ($composeArgs + @("up", "-d", "--build"))

try {
  Wait-ForHttp -Url "http://localhost:8000/health"
  Wait-ForHttp -Url "http://localhost:8001/health"
  Wait-ForHttp -Url "http://localhost:8002/health"
  Wait-ForHttp -Url "http://localhost:8003/health"
  Write-Host "Smoke test passed."
} finally {
  if (-not $Keep) {
    Invoke-Compose ($composeArgs + @("down", "-v"))
  }
}
