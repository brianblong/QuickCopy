param([string]$Python = "py")
$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    & $Python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Could not create the build environment." }
    & .\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
    if ($LASTEXITCODE -ne 0) { throw "Could not install PyInstaller." }
    & .\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name QuickCopy --icon assets/quickcopy.ico --add-data "assets/quickcopy.ico;assets" quickcopy.py
    if ($LASTEXITCODE -ne 0) { throw "Build failed." }
    Write-Host "Ready: $PSScriptRoot\dist\QuickCopy.exe"
} finally {
    Pop-Location
}
