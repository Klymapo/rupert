param(
    [string]$Model = ""
)

$ErrorActionPreference = "Stop"

$Ollama = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $Ollama) {
    Write-Host "❌ Ollama no está instalado o no está en PATH."
    Write-Host "Rupert no lo instala automáticamente: la instalación del runtime debe ser explícita."
    Write-Host "Instala Ollama desde su fuente oficial y vuelve a ejecutar este script."
    exit 1
}

Write-Host "✅ Ollama encontrado: $($Ollama.Source)"

try {
    $version = & ollama --version
    Write-Host $version
} catch {
    Write-Host "⚠️ No pude leer la versión de Ollama."
}

if ($Model) {
    Write-Host ""
    Write-Host "Descargando modelo local: $Model"
    & ollama pull $Model
    if ($LASTEXITCODE -ne 0) { throw "ollama pull terminó con error" }
    Write-Host ""
    Write-Host "✅ Modelo preparado: $Model"
    Write-Host "Configura en .env: OLLAMA_MODEL=$Model"
} else {
    Write-Host ""
    Write-Host "No se descargó ningún modelo. Eso es deliberado: Rupert no fuerza pesos grandes sin conocer tu VRAM/RAM disponible."
    Write-Host "Cuando elijas uno, ejecuta:"
    Write-Host "  .\scripts\setup-ollama.ps1 -Model <modelo>"
}

Write-Host ""
Write-Host "Diagnóstico: .\.venv\Scripts\rupert.exe brain-doctor"
