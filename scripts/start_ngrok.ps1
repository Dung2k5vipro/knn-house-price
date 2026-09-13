$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Ngrok = Join-Path $ProjectRoot "tools\ngrok.exe"

if (-not (Test-Path -LiteralPath $Ngrok)) {
    throw "Không tìm thấy ngrok.exe tại $Ngrok"
}

& $Ngrok http 8000

