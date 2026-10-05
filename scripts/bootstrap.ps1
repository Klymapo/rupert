$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Rupert bootstrap"
Write-Host "======================"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python no está disponible en PATH."
}

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

$Python = Join-Path $Root ".venv\Scripts\python.exe"
& $Python -m pip install --upgrade pip
& $Python -m pip install -e .

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "[!] Creé .env. Pega allí tu OBSIDIAN_API_KEY antes de ejecutar doctor."
}

Write-Host ""
Write-Host "[OK] Bootstrap terminado."
Write-Host "Siguiente: .\.venv\Scripts\rupert.exe doctor"
