# KNN House Price Prediction

Project nay train mo hinh K-Nearest Neighbors Regression tren du lieu nha that, sau do chay FastAPI backend local de du doan gia nha. Backend co Dockerfile de may khac co the build va chay lai cung mot moi truong.

## Kien truc

```text
Kaggle CSV dataset
-> train KNN pipeline
-> luu StandardScaler + KNeighborsRegressor
-> FastAPI load model local
-> Swagger/Postman goi prediction
-> Docker chay tren may khac
```

Dataset dang dung: `backend/data/house_data1.csv`.

Dataset goc co cac cot `price`, `bedrooms`, `sqft_living`, `lat`, `long`. Project chuyen ve 3 feature dung cho bai KNN:

```text
area      = sqft_living doi sang m2
rooms     = bedrooms
distance  = khoang cach km toi trung tam Seattle
price     = gia nha trong dataset goc, don vi USD
```

## Chay local bang Python

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python training/train.py
uvicorn app.main:app --reload --port 8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Chay bang Docker

Docker build se tu train model tu file CSV trong `backend/data/house_data1.csv`.

```powershell
cd backend
docker build -t knn-house-backend .
docker run --rm -p 8000:8000 knn-house-backend
```

Mo Swagger:

```text
http://localhost:8000/docs
```

## Public URL bang Ngrok

Ngrok da duoc cai local trong thu muc `tools/`. Truoc khi demo, them authtoken mot lan:

```powershell
.\scripts\setup_ngrok.ps1 "<NGROK_AUTHTOKEN_CUA_BAN>"
```

Chay backend Docker o terminal thu nhat:

```powershell
.\scripts\start_backend_docker.ps1
```

Mo terminal thu hai va public port `8000`:

```powershell
.\scripts\start_ngrok.ps1
```

Ngrok se in URL dang:

```text
https://xxxx.ngrok-free.app
```

Gui link nay cho may trinh chieu:

```text
https://xxxx.ngrok-free.app/docs
```

## API

Health check:

```http
GET /health
```

Prediction:

```http
POST /api/v1/predict
```

Request:

```json
{
  "area": 109.63,
  "rooms": 3,
  "distance": 18.5
}
```

Response:

```json
{
  "success": true,
  "input": {
    "area": 109.63,
    "rooms": 3,
    "distance": 18.5
  },
  "predicted_price": 315000.0,
  "unit": "usd"
}
```

## Chay test

```powershell
cd backend
pytest -q
```

## Dua cho may khac chay

May khac chi can clone repo, cai Docker, roi chay:

```powershell
cd backend
docker build -t knn-house-backend .
docker run --rm -p 8000:8000 knn-house-backend
```

Neu muon gui URL public tren Internet, co the deploy Docker image len server/cloud hoac dung tunnel. Con neu cung mang LAN, chay container tren may cua ban va gui dia chi IP noi bo kem port `8000`.
