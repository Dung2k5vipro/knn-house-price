# CODEX.md

# KNN House Price Prediction

## 1. Vai trò của file này

`CODEX.md` là tài liệu hướng dẫn chính cho Coding Agent khi làm project.

Agent phải đọc toàn bộ file này trước khi tạo hoặc sửa source code.

Nguyên tắc quan trọng nhất:

- Làm theo từng bước lớn.
- Bước nào bắt đầu thì phải làm hoàn chỉnh bước đó.
- Không để `TODO`, file rỗng, function rỗng hoặc code dang dở trong phạm vi bước đang làm.
- Phải chạy thử / kiểm tra trước khi chuyển sang bước tiếp theo.
- Chỉ chuyển bước khi người dùng yêu cầu.
- Không tự ý thay đổi architecture.
- Không over-engineer.
- Không thêm database, frontend, Redis, Kafka, authentication, Kubernetes hoặc các thành phần không được yêu cầu.

---

# 2. Mục tiêu project

Xây dựng project môn **Học máy cơ bản** với chủ đề:

**K-Nearest Neighbors (KNN)**

Bài toán:

**Dự đoán giá nhà bằng K-Nearest Neighbors Regression**

Model có 3 input:

```text
area
rooms
distance
```

Ý nghĩa:

```text
area      = diện tích nhà (m²)
rooms     = số phòng
distance  = khoảng cách tới trung tâm (km)
```

Output:

```text
predicted_price
```

Đơn vị giá:

```text
triệu VNĐ
```

---

# 3. Loại bài toán

Đây là bài toán Regression.

Không dùng:

```python
KNeighborsClassifier
```

Phải dùng:

```python
KNeighborsRegressor
```

vì output là giá nhà, tức là giá trị liên tục.

---

# 4. Architecture cuối cùng

Project có 2 thành phần chính.

## Thành phần 1 — Model Server trên Google Colab

Google Colab chịu trách nhiệm:

```text
Dataset
↓
Tiền xử lý
↓
StandardScaler
↓
KNeighborsRegressor
↓
Train
↓
Evaluate
↓
Chọn K phù hợp
↓
Save model
↓
Load model
↓
FastAPI Model Server
↓
Ngrok
↓
Public URL
```

Model Server nhận request:

```json
{
  "area": 85.5,
  "rooms": 3,
  "distance": 5.2
}
```

và trả response:

```json
{
  "predicted_price": 2450.7
}
```

## Thành phần 2 — FastAPI Backend trên máy cá nhân

Backend chạy trên máy cá nhân bằng:

```text
Python
venv
FastAPI
Uvicorn
Pydantic
httpx
```

Backend có nhiệm vụ:

```text
Postman / Client
↓
FastAPI Backend
↓
Validate input
↓
Gọi Model Server qua Ngrok
↓
Nhận predicted_price
↓
Trả kết quả lại cho client
```

Backend local không tự train model và không tự load KNN model để predict trong architecture cuối cùng.

---

# 5. Docker

Backend trên máy cá nhân phải được đóng gói bằng Docker.

Quy trình:

```text
Backend chạy bằng venv
↓
Test local thành công
↓
Dockerfile
↓
docker build
↓
docker run
↓
Test lại bằng Postman
```

Docker giúp máy khác có thể clone GitHub, build image và run container mà không cần cài thủ công toàn bộ dependency Python.

---

# 6. Architecture Diagram

```text
                         POSTMAN / CLIENT
                                |
                                v
                    +-----------------------+
                    |   FASTAPI BACKEND     |
                    |    máy cá nhân        |
                    | - validate input      |
                    | - call model server   |
                    | - handle errors       |
                    +-----------+-----------+
                                |
                                | HTTP POST
                                v
                    +-----------------------+
                    |      NGROK URL        |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    |    GOOGLE COLAB       |
                    | FASTAPI MODEL SERVER  |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    | StandardScaler        |
                    | KNeighborsRegressor   |
                    +-----------+-----------+
                                |
                                v
                         predicted_price
```

---

# 7. Project Structure

```text
knn-house-price/
│
├── CODEX.md
├── README.md
├── .gitignore
│
├── model_server/
│   └── colab/
│       └── knn_house_model.ipynb
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── config.py
│   │   └── model_client.py
│   │
│   ├── tests/
│   │   └── test_api.py
│   │
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── .dockerignore
│
└── docs/
    └── architecture.md
```

Không tự ý tạo thêm nhiều tầng thư mục nếu chưa cần.

---

# 8. Dataset

Phiên bản đầu tiên có thể dùng synthetic dataset.

Các column:

```text
area
rooms
distance
price
```

Ví dụ:

```csv
area,rooms,distance,price
80,3,5,2500
65,2,12,1700
120,4,3,3900
```

Đơn vị:

```text
area      = m²
rooms     = số phòng
distance  = km
price     = triệu VNĐ
```

Có thể tạo khoảng 500–1000 samples và phải có noise.

---

# 9. Feature và Target

```text
X = [area, rooms, distance]
y = price
```

---

# 10. StandardScaler

KNN dựa vào khoảng cách nên phải scale dữ liệu.

Phải dùng:

```python
StandardScaler
```

và nên đóng scaler + KNN vào cùng `Pipeline`:

```python
Pipeline([
    ("scaler", StandardScaler()),
    ("knn", KNeighborsRegressor(n_neighbors=5))
])
```

---

# 11. Train / Test Split

Dùng:

```python
train_test_split
```

Tỉ lệ:

```text
80% train
20% test
```

Sử dụng:

```python
random_state=42
```

---

# 12. Chọn K

Không được chọn K tùy ý rồi kết thúc.

Phải thử nhiều giá trị, ví dụ:

```text
1, 3, 5, 7, 9, 11, 15
```

Với mỗi K:

```text
Train
↓
Predict
↓
Evaluate
```

Sau đó chọn K tốt nhất và giải thích ngắn gọn lý do.

---

# 13. Metrics

Vì là Regression, phải đánh giá bằng:

```text
MAE
RMSE
R²
```

---

# 14. Save / Load Model

Sau khi chọn K tốt nhất, lưu cả Pipeline bằng:

```python
joblib.dump(...)
```

Tên model:

```text
knn_house_model.pkl
```

Khi inference:

```python
joblib.load(...)
```

Không train lại model khi `/predict` được gọi.

---

# 15. Model Server trên Colab

Dùng:

```text
FastAPI
Uvicorn
```

Endpoint:

```http
GET /health
```

Response:

```json
{
  "status": "ok",
  "service": "knn-house-model-server"
}
```

Prediction:

```http
POST /predict
```

Request:

```json
{
  "area": 85.5,
  "rooms": 3,
  "distance": 5.2
}
```

Response:

```json
{
  "predicted_price": 2450.7
}
```

Validation:

```text
area > 0
rooms >= 1
distance >= 0
```

---

# 16. Google Colab Notebook

Notebook:

```text
model_server/colab/knn_house_model.ipynb
```

Các cell nên theo thứ tự:

```text
Cell 1  - Install dependencies
Cell 2  - Imports
Cell 3  - Create / Load dataset
Cell 4  - Inspect dataset
Cell 5  - Create X / y
Cell 6  - Train/test split
Cell 7  - Try multiple K values
Cell 8  - Compare metrics
Cell 9  - Select best K
Cell 10 - Train final Pipeline
Cell 11 - Evaluate final model
Cell 12 - Save model
Cell 13 - Load model
Cell 14 - Test prediction
Cell 15 - Define FastAPI schemas
Cell 16 - Create FastAPI Model Server
Cell 17 - Start Uvicorn
Cell 18 - Configure Ngrok
Cell 19 - Print public URL
```

Notebook phải chạy được từ trên xuống dưới.

---

# 17. Ngrok

Model Server trên Colab chạy ở port 8000 và được public bằng Ngrok.

Ví dụ:

```text
https://xxxx.ngrok-free.app
```

Prediction endpoint:

```text
https://xxxx.ngrok-free.app/predict
```

Không hard-code Ngrok auth token.

Không commit token lên GitHub.

---

# 18. Backend FastAPI trên máy cá nhân

Endpoint:

```http
GET /health
POST /api/v1/predict
```

Request:

```json
{
  "area": 85.5,
  "rooms": 3,
  "distance": 5.2
}
```

Backend forward dữ liệu tới:

```text
{MODEL_SERVER_URL}/predict
```

Response:

```json
{
  "success": true,
  "input": {
    "area": 85.5,
    "rooms": 3,
    "distance": 5.2
  },
  "predicted_price": 2450.7
}
```

---

# 19. Environment Variables

Tạo:

```text
backend/.env
```

Ví dụ:

```env
MODEL_SERVER_URL=https://xxxx.ngrok-free.app
MODEL_SERVER_TIMEOUT=10
```

Tạo thêm:

```text
backend/.env.example
```

`.env` phải nằm trong `.gitignore`.

---

# 20. Backend HTTP Client

Dùng:

```python
httpx.AsyncClient
```

Phải có timeout và error handling.

Lỗi tối thiểu:

```text
422 - input không hợp lệ
503 - không kết nối được Model Server
504 - Model Server timeout
502 - Model Server trả lỗi / response không hợp lệ
```

---

# 21. venv

Backend phải chạy bằng venv trước Docker.

Windows:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# 22. requirements.txt

Tối thiểu:

```text
fastapi
uvicorn[standard]
httpx
pydantic
pydantic-settings
python-dotenv
pytest
```

---

# 23. Docker

Chỉ Dockerize backend local.

Build:

```bash
cd backend
docker build -t knn-house-backend .
```

Run:

```bash
docker run --rm -p 8000:8000 --env-file .env knn-house-backend
```

Swagger:

```text
http://localhost:8000/docs
```

Máy khác có Docker có thể clone repo, tạo `.env`, build image và run container.

---

# 24. Postman Test Flow

## Test 1 — Model Server trực tiếp

```http
POST https://NGROK_MODEL_URL/predict
```

## Test 2 — Backend local

```http
POST http://127.0.0.1:8000/api/v1/predict
```

## Test 3 — Backend Docker

```http
POST http://localhost:8000/api/v1/predict
```

Body:

```json
{
  "area": 85.5,
  "rooms": 3,
  "distance": 5.2
}
```

---

# 25. GitHub

Không push:

```text
.env
Ngrok token
.venv
venv
__pycache__
*.pyc
```

Phải push:

```text
CODEX.md
README.md
.gitignore
model_server/
backend/
docs/
```

---

# 26. README cuối cùng

README phải có:

1. tên project;
2. mục tiêu bài toán;
3. giới thiệu KNN;
4. vì sao dùng KNeighborsRegressor;
5. input/output;
6. dataset;
7. StandardScaler;
8. cách chọn K;
9. MAE/RMSE/R²;
10. architecture;
11. cách chạy Colab;
12. Ngrok;
13. backend venv;
14. Postman;
15. Docker;
16. cách chạy trên máy khác;
17. ví dụ request/response.

---

# 27. Quy tắc làm việc theo từng bước

Project chia thành 6 bước lớn.

**Bước nào bắt đầu thì phải hoàn chỉnh toàn bộ bước đó trước khi sang bước tiếp theo.**

---

# BƯỚC 1 — Khởi tạo project + GitHub

Hoàn chỉnh:

```text
README.md
.gitignore
CODEX.md
model_server/colab/
backend/
docs/
Git repository
commit đầu tiên
push GitHub
```

Bước 1 chỉ hoàn thành khi source đã có trên GitHub.

Sau đó dừng.

---

# BƯỚC 2 — Machine Learning hoàn chỉnh trên Colab

Hoàn chỉnh:

```text
Dataset
↓
X / y
↓
train_test_split
↓
StandardScaler
↓
KNeighborsRegressor
↓
thử nhiều K
↓
chọn K tốt nhất
↓
MAE
↓
RMSE
↓
R²
↓
train final Pipeline
↓
save model
↓
load model
↓
predict thử
```

Notebook phải chạy từ đầu đến cuối.

Sau đó dừng.

---

# BƯỚC 3 — Model Server + Ngrok hoàn chỉnh

Hoàn chỉnh:

```text
FastAPI Model Server
GET /health
POST /predict
Pydantic validation
load model
predict
Ngrok
public URL
Postman test
```

Bước 3 chỉ hoàn thành khi Postman gọi trực tiếp URL Ngrok và nhận prediction thành công.

Sau đó dừng.

---

# BƯỚC 4 — Backend FastAPI local + venv hoàn chỉnh

Hoàn chỉnh:

```text
backend/app/
requirements.txt
.env.example
venv
GET /health
POST /api/v1/predict
validation
httpx
error handling
Swagger
Postman test
```

Bước 4 chỉ hoàn thành khi:

```text
Postman
↓
FastAPI local
↓
Ngrok
↓
Colab Model Server
↓
prediction
```

chạy thành công.

Sau đó dừng.

---

# BƯỚC 5 — Docker hoàn chỉnh

Hoàn chỉnh:

```text
Dockerfile
.dockerignore
docker build
docker run
Swagger
Postman
```

Bước 5 chỉ hoàn thành khi:

```text
Postman
↓
Docker FastAPI Backend
↓
Ngrok
↓
Colab Model Server
↓
prediction
```

chạy thành công.

Sau đó dừng.

---

# BƯỚC 6 — Documentation + GitHub final

Hoàn thiện:

```text
README.md
docs/architecture.md
Docker instructions
Postman examples
Architecture diagram
final commit
final push GitHub
```

Kiểm tra không có secret.

---

# 28. Quy tắc Coding Agent

Trước khi code:

1. Đọc `CODEX.md`.
2. Kiểm tra source hiện tại.
3. Xác định bước đang làm.
4. Không làm sang bước khác.

Trong khi code:

1. Tạo file hoàn chỉnh.
2. Không để TODO cho logic chính.
3. Không để function `pass`.
4. Không hard-code secret.
5. Giữ đúng architecture.

Sau khi code:

1. chạy kiểm tra;
2. sửa lỗi;
3. liệt kê file đã tạo/sửa;
4. giải thích ngắn gọn;
5. đưa lệnh chạy;
6. xác nhận tiêu chí hoàn thành;
7. dừng lại.

---

# 29. Prompt khởi động cho Antigravity / Codex

```text
Đọc toàn bộ file CODEX.md trong workspace.

CODEX.md là source of truth của project KNN House Price Prediction.

Project đang bắt đầu từ đầu.

Hãy bắt đầu BƯỚC 1 và hoàn chỉnh toàn bộ BƯỚC 1.

Yêu cầu:
- kiểm tra workspace hiện tại;
- tạo đúng project structure trong CODEX.md;
- tạo README.md và .gitignore;
- giữ nguyên CODEX.md;
- chuẩn bị Git repository;
- không viết Machine Learning ở bước này;
- không tạo Model Server;
- không tạo Dockerfile;
- không làm BƯỚC 2;
- kiểm tra lại project sau khi hoàn thành;
- liệt kê toàn bộ file/thư mục vừa tạo;
- đưa lệnh Git cần chạy để commit và push GitHub;
- sau đó dừng lại.

Không chuyển sang bước tiếp theo cho đến khi tôi yêu cầu.
```

---

# 30. Prompt tiếp tục

```text
Đọc lại CODEX.md.
Kiểm tra source hiện tại.
Tiếp tục BƯỚC X.
Hoàn chỉnh toàn bộ BƯỚC X, chạy kiểm tra và dừng lại sau khi bước đó hoàn thành.
Không làm bước tiếp theo.
```

---

# 31. Definition of Done

Project hoàn thành khi:

```text
Google Colab
↓
KNN model train thành công
↓
StandardScaler + KNeighborsRegressor
↓
MAE / RMSE / R²
↓
Model Server FastAPI
↓
Ngrok public URL
↓
FastAPI Backend local
↓
Docker Backend
↓
Postman gọi prediction thành công
```

Architecture cuối:

```text
Postman
↓
Docker FastAPI Backend
↓
Ngrok
↓
Google Colab Model Server
↓
KNeighborsRegressor
↓
Predicted Price
↓
Backend
↓
Postman
```
