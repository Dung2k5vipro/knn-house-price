param(
    [Parameter(Mandatory = $true)]
    [string]$Authtoken
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Ngrok = Join-Path $ProjectRoot "tools\ngrok.exe"

if (-not (Test-Path -LiteralPath $Ngrok)) {
    throw "Không tìm thấy ngrok.exe tại $Ngrok"
}

& $Ngrok config add-authtoken $Authtoken

