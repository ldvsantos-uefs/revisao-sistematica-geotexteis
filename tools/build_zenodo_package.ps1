Param(
    [string]$OutputDir = "dist/zenodo-package",
    [string]$ZipPath = "dist/zenodo-package.zip"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$outDir = Join-Path $repoRoot $OutputDir
$zipFile = Join-Path $repoRoot $ZipPath

function Ensure-EmptyDir([string]$path) {
    if (Test-Path $path) {
        Remove-Item -Recurse -Force $path
    }
    New-Item -ItemType Directory -Path $path | Out-Null
}

function Copy-IfExists([string]$src, [string]$dst) {
    if (Test-Path $src) {
        New-Item -ItemType Directory -Path $dst -Force | Out-Null
        Copy-Item -Recurse -Force $src $dst
    }
}

Ensure-EmptyDir $outDir

# 1) Scripts
$srcScripts = Join-Path $repoRoot "4-CODIGOS"
$dstScripts = Join-Path $outDir "scripts"
if (Test-Path $srcScripts) {
    New-Item -ItemType Directory -Path $dstScripts -Force | Out-Null
    Copy-Item -Force (Join-Path $srcScripts "*.py") $dstScripts -ErrorAction SilentlyContinue
    Copy-Item -Force (Join-Path $srcScripts "*.R")  $dstScripts -ErrorAction SilentlyContinue
}

# 2) Dados (apenas planilhas comuns: csv/xlsx/xls)
$srcData = Join-Path $repoRoot "5-DADOS"
$dstData = Join-Path $outDir "data"
if (Test-Path $srcData) {
    New-Item -ItemType Directory -Path $dstData -Force | Out-Null

    $srcDataResolved = (Resolve-Path $srcData).Path

    $extensions = @(".csv", ".xlsx", ".xls")
    Get-ChildItem -Path $srcData -Recurse -File | ForEach-Object {
        if ($extensions -contains $_.Extension.ToLowerInvariant()) {
            $full = (Resolve-Path $_.FullName).Path
            $relative = $full.Substring($srcDataResolved.Length).TrimStart('\','/')
            $destPath = Join-Path $dstData $relative
            $destFolder = Split-Path -Parent $destPath
            New-Item -ItemType Directory -Path $destFolder -Force | Out-Null
            Copy-Item -Force $_.FullName $destPath
        }
    }
}

# 3) Metadados básicos para o depósito
$readme = @'
Pacote para depósito no Zenodo

Conteúdo
- scripts/: scripts de análise (Python/R)
- data/: planilhas e tabelas (CSV/XLS/XLSX)

Observações
- Este pacote foi gerado a partir do repositório do artigo e inclui apenas scripts e planilhas.
- Se você precisar incluir arquivos adicionais (ex.: dicionário de dados, outputs), adicione manualmente antes de enviar ao Zenodo.

Como gerar
- Execute: powershell -ExecutionPolicy Bypass -File tools/build_zenodo_package.ps1

'@
Set-Content -Encoding UTF8 -Path (Join-Path $outDir "README.txt") -Value $readme

# 4) Compactar
$zipDir = Split-Path -Parent $zipFile
if (-not (Test-Path $zipDir)) { New-Item -ItemType Directory -Path $zipDir | Out-Null }
if (Test-Path $zipFile) { Remove-Item -Force $zipFile }
Compress-Archive -Path (Join-Path $outDir "*") -DestinationPath $zipFile

Write-Output "OK: pacote criado em: $zipFile"
Write-Output "OK: pasta staging: $outDir"
