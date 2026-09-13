# Architecture

Huong moi cua project:

```text
              +---------------------------+
              | backend/data/house_data1.csv |
              +-------------+-------------+
                            |
                            v
              +---------------------------+
              | training/train.py         |
              | - clean data              |
              | - create area/rooms/distance |
              | - try many K values       |
              | - evaluate MAE/RMSE/R2    |
              +-------------+-------------+
                            |
                            v
              +---------------------------+
              | models/knn_house_model.pkl |
              | StandardScaler + KNN      |
              +-------------+-------------+
                            |
                            v
              +---------------------------+
              | FastAPI backend           |
              | GET /health               |
              | POST /api/v1/predict      |
              +-------------+-------------+
                            |
                            v
              +---------------------------+
              | Swagger / Postman / Client |
              +---------------------------+
```

Docker build chay `python training/train.py`, vi vay image tu tao model tu dataset va san sang phuc vu du doan.

Input API:

```text
area      m2
rooms     so phong ngu
distance  km toi trung tam Seattle
```

Output:

```text
predicted_price, don vi USD theo dataset goc
```

