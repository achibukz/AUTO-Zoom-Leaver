[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $RepoRoot ".venv-build"
$PythonPath = Join-Path $VenvPath "Scripts\python.exe"
$SpecPath = Join-Path $RepoRoot "tools\windows_auto_leaver.spec"
$DistPath = Join-Path $RepoRoot "dist"
$BuildPath = Join-Path $RepoRoot "build"

function Invoke-BuildStage {
    param(
        [Parameter(Mandatory = $true)] [string] $Name,
        [Parameter(Mandatory = $true)] [scriptblock] $Action
    )

    Write-Host "==> $Name" -ForegroundColor Cyan
    $global:LASTEXITCODE = 0
    try {
        & $Action
        if ($LASTEXITCODE -ne 0) {
            throw "command exited with code $LASTEXITCODE"
        }
    }
    catch {
        throw "Stage failed: $Name. $($_.Exception.Message)"
    }
}

try {
    Push-Location $RepoRoot

    Invoke-BuildStage "create clean build environment" {
        if (Test-Path $VenvPath) {
            Remove-Item $VenvPath -Recurse -Force
        }
        & python -m venv $VenvPath
    }

    Invoke-BuildStage "install pinned dependencies" {
        & $PythonPath -m pip install --requirement (Join-Path $RepoRoot "requirements_windows.txt")
    }

    Invoke-BuildStage "run tests" {
        & $PythonPath -m pytest -q
    }

    Invoke-BuildStage "build and validate onedir artifact" {
        $env:AUTO_ZOOM_LEAVER_BUILD_MODE = "onedir"
        & $PythonPath -m PyInstaller --noconfirm --clean --distpath $DistPath --workpath (Join-Path $BuildPath "onedir") $SpecPath
        $oneDirExecutable = Join-Path $DistPath "AutoZoomLeaver\AutoZoomLeaver.exe"
        if (-not (Test-Path $oneDirExecutable)) {
            throw "onedir artifact was not created at $oneDirExecutable"
        }
    }

    Invoke-BuildStage "build and validate onefile artifact" {
        $env:AUTO_ZOOM_LEAVER_BUILD_MODE = "onefile"
        & $PythonPath -m PyInstaller --noconfirm --clean --distpath $DistPath --workpath (Join-Path $BuildPath "onefile") $SpecPath
        $oneFileExecutable = Join-Path $DistPath "AutoZoomLeaver.exe"
        if (-not (Test-Path $oneFileExecutable)) {
            throw "onefile artifact was not created at $oneFileExecutable"
        }
    }

    Write-Host "Build complete: $DistPath\AutoZoomLeaver.exe" -ForegroundColor Green
}
catch {
    Write-Error $_
    exit 1
}
finally {
    Remove-Item Env:AUTO_ZOOM_LEAVER_BUILD_MODE -ErrorAction SilentlyContinue
    if ((Get-Location).Path -eq $RepoRoot) {
        Pop-Location
    }
}
