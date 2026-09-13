$ProjectRoot = Split-Path -Parent $PSScriptRoot
$BackendRoot = Join-Path $ProjectRoot "backend"

Set-Location $BackendRoot

docker build -t knn-house-backend .
docker run --rm -p 8000:8000 --name knn-house-backend-demo knn-house-backend

