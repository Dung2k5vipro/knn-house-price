from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    area: float = Field(..., gt=0, description="House living area in square meters")
    rooms: int = Field(..., ge=1, description="Number of bedrooms")
    distance: float = Field(..., ge=0, description="Distance to Seattle center in kilometers")


class PredictionInput(BaseModel):
    area: float
    rooms: int
    distance: float


class PredictionResponse(BaseModel):
    success: bool
    input: PredictionInput
    predicted_price: float
    unit: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model: str
    best_k: int | None = None
    training_rows: int | None = None

