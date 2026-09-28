$ErrorActionPreference = "Stop"
$Venv = if ($env:VENV_DIR) { $env:VENV_DIR } else { ".venv" }

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { throw "Python 3.11+ is required. Install Python and rerun this script." }

$version = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$parts = $version.Split('.') | ForEach-Object { [int]$_ }
if (($parts[0] -lt 3) -or (($parts[0] -eq 3) -and ($parts[1] -lt 11))) { throw "Python 3.11+ is required." }

python -m venv $Venv
& "$Venv\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel
& "$Venv\Scripts\python.exe" -m pip install -e ".[all,dev]"
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }

if ((-not (Test-Path .env)) -and (Test-Path .env.example)) { Copy-Item .env.example .env }

& "$Venv\Scripts\python.exe" -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Installation verification failed: tests did not pass." }
Write-Host "`nAdaptiveRAG-X is installed."
Write-Host "Start API: .\$Venv\Scripts\adaptive-rag-api.exe"
Write-Host "Research: .\$Venv\Scripts\adaptive-rag.exe research 'your question'"
