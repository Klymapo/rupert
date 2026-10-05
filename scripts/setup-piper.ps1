param(
    [string]$Voice = "es_MX-ald-medium",
    [switch]$Cuda
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$DataDir = Join-Path $RepoRoot ".runtime\models\piper"

if (-not (Test-Path $Python)) {
    throw "No encuentro .venv. Ejecuta primero .\scripts\bootstrap.ps1"
}

New-Item -ItemType Directory -Force -Path $DataDir | Out-Null

Push-Location $RepoRoot
try {
    Write-Host "[1/3] Instalando extras locales de audio + Piper..."
    & $Python -m pip install -e ".[full]"
    if ($LASTEXITCODE -ne 0) { throw "Falló pip install" }

    if ($Cuda) {
        Write-Host "[2/3] Instalando runtime CUDA opcional para Piper..."
        & $Python -m pip install onnxruntime-gpu
        if ($LASTEXITCODE -ne 0) { throw "Falló onnxruntime-gpu" }
    } else {
        Write-Host "[2/3] CUDA para TTS omitido (CPU es suficiente para empezar)."
    }

    Write-Host "[3/3] Descargando voz $Voice a .runtime (fuera de Git)..."
    & $Python -m piper.download_voices --data-dir $DataDir $Voice
    if ($LASTEXITCODE -ne 0) { throw "Falló descarga de la voz Piper" }
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "✅ Piper preparado."
Write-Host "Voz: $Voice"
Write-Host "Datos: $DataDir"
Write-Host "Prueba: .\.venv\Scripts\rupert.exe tts-doctor"
Write-Host "Habla:  .\.venv\Scripts\rupert.exe speak `"Rupert está en línea.`""
