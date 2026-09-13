from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status

from app.model import MODEL_NAME, HousePriceModel
from app.schemas import HealthResponse, PredictionRequest, PredictionResponse


house_model = HousePriceModel()


@asynccontextmanager
async def lifespan(_: FastAPI):
    house_model.load()
    yield


app = FastAPI(
    title="KNN House Price Prediction API",
    version="1.0.0",
    description="FastAPI backend loading a trained KNN regression pipeline from local disk.",
    lifespan=lifespan,
)


@app.get("/")
def root() -> dict[str, object]:
    return {
        "service": "knn-house-price-api",
        "docs": "/docs",
        "health": "/health",
        "predict": "/api/v1/predict",
    }


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="healthy" if house_model.is_loaded else "unhealthy",
        model_loaded=house_model.is_loaded,
        model=MODEL_NAME,
        best_k=house_model.metadata.get("best_k"),
        training_rows=house_model.metadata.get("training_rows"),
    )


@app.post("/api/v1/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> PredictionResponse:
    try:
        predicted_price = house_model.predict(
            area=request.area,
            rooms=request.rooms,
            distance=request.distance,
        )
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error

    return PredictionResponse(
        success=True,
        input=request.model_dump(),
        predicted_price=predicted_price,
        unit=house_model.metadata.get("price_unit", "usd"),
    )


@app.post("/predict", response_model=PredictionResponse)
def predict_short(request: PredictionRequest) -> PredictionResponse:
    return predict(request)
