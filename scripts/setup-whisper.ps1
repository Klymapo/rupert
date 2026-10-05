param(
    [switch]$Cuda,
    [switch]$SkipBuild,
    [ValidateSet("tiny","base","small")][string]$Model = "base"
)
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Runtime = Join-Path $Root ".runtime"
$Vendor = Join-Path $Runtime "vendors\whisper.cpp"
$Models = Join-Path $Runtime "models\whisper"
$Tag = "v1.9.4"

New-Item -ItemType Directory -Force -Path (Split-Path $Vendor), $Models | Out-Null

if (-not $SkipBuild) {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "Git no está disponible." }
    if (-not (Get-Command cmake -ErrorAction SilentlyContinue)) { throw "CMake no está disponible." }
    if (-not (Test-Path (Join-Path $Vendor ".git"))) {
        git clone --depth 1 --branch $Tag https://github.com/ggml-org/whisper.cpp.git $Vendor
    } else {
        git -C $Vendor fetch --depth 1 origin tag $Tag
        git -C $Vendor checkout $Tag
    }
    $cmakeArgs = @("-S", $Vendor, "-B", (Join-Path $Vendor "build"), "-DCMAKE_BUILD_TYPE=Release")
    if ($Cuda) { $cmakeArgs += "-DGGML_CUDA=ON" }
    & cmake @cmakeArgs
    & cmake --build (Join-Path $Vendor "build") --config Release -j
}

$ModelFile = Join-Path $Models "ggml-$Model.bin"
if (-not (Test-Path $ModelFile)) {
    $url = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-$Model.bin"
    Write-Host "Descargando modelo $Model..."
    Invoke-WebRequest -Uri $url -OutFile $ModelFile
}

Write-Host ""
Write-Host "Rupert voice listo."
Write-Host "Modelo: $ModelFile"
Write-Host "Prueba: .\.venv\Scripts\rupert.exe voice-doctor"
