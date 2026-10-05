param(
    [switch]$DownloadSmokeModel
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$ModelDir = Join-Path $RepoRoot ".runtime\models\wakeword"

if (-not (Test-Path $Python)) {
    throw "No encuentro .venv. Ejecuta primero .\scripts\bootstrap.ps1"
}

New-Item -ItemType Directory -Force -Path $ModelDir | Out-Null

Push-Location $RepoRoot
try {
    Write-Host "[1/2] Instalando openWakeWord 0.6.0 + captura local..."
    & $Python -m pip install -e ".[wake]"
    if ($LASTEXITCODE -ne 0) { throw "Falló pip install" }

    if ($DownloadSmokeModel) {
        Write-Host "[2/2] Descargando modelo de prueba 'hey_jarvis'..."
        $code = "import openwakeword.utils; openwakeword.utils.download_models(model_names=['hey_jarvis_v0.1'], target_directory=r'$ModelDir')"
        & $Python -c $code
        if ($LASTEXITCODE -ne 0) { throw "Falló la descarga del modelo de prueba" }
        Write-Host ""
        Write-Host "Modelo de humo: $ModelDir\hey_jarvis_v0.1.onnx"
        Write-Host "Puedes apuntar WAKEWORD_MODEL temporalmente a ese archivo."
    } else {
        Write-Host "[2/2] Modelo de humo omitido."
    }
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "✅ Capa wake-word preparada."
Write-Host "Para 'Rupert', coloca el ONNX personalizado en:"
Write-Host "  $ModelDir\rupert.onnx"
Write-Host "Después ejecuta: .\.venv\Scripts\rupert.exe wake-doctor"
