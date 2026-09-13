from fastapi.testclient import TestClient

from training.train import MODEL_PATH, train_model


if not MODEL_PATH.exists():
    train_model()

from app.main import app  # noqa: E402


def test_health_and_prediction() -> None:
    with TestClient(app) as client:
        health_response = client.get("/health")
        prediction_response = client.post(
            "/api/v1/predict",
            json={"area": 109.63, "rooms": 3, "distance": 18.5},
        )

    assert health_response.status_code == 200
    health_body = health_response.json()
    assert health_body["status"] == "healthy"
    assert health_body["model_loaded"] is True
    assert health_body["model"] == "knn_house_price_regressor"
    assert isinstance(health_body["best_k"], int)

    assert prediction_response.status_code == 200
    body = prediction_response.json()
    assert body["success"] is True
    assert body["input"] == {"area": 109.63, "rooms": 3, "distance": 18.5}
    assert body["predicted_price"] > 0
    assert body["unit"] == "usd"


def test_invalid_input_is_rejected() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/predict",
            json={"area": -1, "rooms": 0, "distance": -3},
        )

    assert response.status_code == 422

