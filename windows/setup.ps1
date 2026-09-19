# One-time setup for the mem0 MCP server on Windows.
# Usage:  powershell -ExecutionPolicy Bypass -File windows\setup.ps1
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$VenvPy = Join-Path $RepoRoot "venv\Scripts\python.exe"

Write-Host "==> Creating Python 3.12 venv at $RepoRoot\venv"
py -3.12 -m venv "$RepoRoot\venv"
& $VenvPy -m pip install --upgrade pip
& $VenvPy -m pip install -r "$RepoRoot\mem0\requirements.txt"

Write-Host "==> Creating data directories under C:\mem0"
New-Item -ItemType Directory -Force -Path "C:\mem0\mem0_data" | Out-Null

Write-Host "==> Verifying qdrant data dir"
if (-not (Test-Path "C:\mem0\.qdrant_data\collections")) {
    Write-Warning "C:\mem0\.qdrant_data\collections not found. Extract the migration tarball first (see windows\README.md)."
}

Write-Host "Setup complete. Next: edit windows\mem0.env (DeepSeek key), then run windows\start-all.ps1"
