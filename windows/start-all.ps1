# Starts the local mem0 stack: qdrant (Docker) + mem0 MCP server (venv python).
# Prerequisite: a llama.cpp embeddings instance listening on 127.0.0.1:8084.
# Usage:  powershell -ExecutionPolicy Bypass -File windows\start-all.ps1
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$QdrantData = "C:\mem0\.qdrant_data"

# 1) Check llama.cpp embeddings endpoint (port 8084)
$embedUp = Test-NetConnection -ComputerName 127.0.0.1 -Port 8084 -InformationLevel Quiet -WarningAction SilentlyContinue
if (-not $embedUp) {
    Write-Warning "Embeddings endpoint 127.0.0.1:8084 is not up. Start it first, e.g.:"
    Write-Warning "  llama-server -m embeddinggemma-300M-Q8_0.gguf --embeddings --port 8084 --alias embeddinggemma-300M"
    exit 1
}

# 2) Qdrant via Docker
if (docker ps -a --format "{{.Names}}" | Select-String -SimpleMatch "qdrant_local") {
    Write-Host "==> Starting existing qdrant_local container"
    docker start qdrant_local | Out-Null
} else {
    if (-not (Test-Path (Join-Path $QdrantData "collections"))) {
        throw "Qdrant data dir not found: $QdrantData (extract the migration tarball first, see windows\README.md)"
    }
    Write-Host "==> Creating qdrant container"
    docker run -d --name qdrant_local --restart unless-stopped -p 7333:6333 -p 7334:6334 -v "${QdrantData}:/qdrant/storage" qdrant/qdrant:latest | Out-Null
}

Write-Host "==> Waiting for qdrant on port 7333..."
$ok = $false
for ($i = 0; $i -lt 30; $i++) {
    if (Test-NetConnection -ComputerName 127.0.0.1 -Port 7333 -InformationLevel Quiet -WarningAction SilentlyContinue) { $ok = $true; break }
    Start-Sleep -Seconds 1
}
if (-not $ok) { throw "Qdrant did not come up on port 7333" }

# 3) mem0 MCP server (foreground; env loaded from windows\mem0.env)
Get-Content (Join-Path $PSScriptRoot "mem0.env") | ForEach-Object {
    if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$') {
        Set-Item -Path "env:$($matches[1])" -Value $matches[2]
    }
}

Write-Host "==> Starting mem0 MCP server on 127.0.0.1:8090/mcp (Ctrl+C to stop)"
& "$RepoRoot\venv\Scripts\python.exe" "$RepoRoot\mem0\server.py"
