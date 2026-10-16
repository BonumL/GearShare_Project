from fastapi.testclient import TestClient

from app.main import app


def test_health_retourne_all_good(client: TestClient) -> None:
    """Vérifie la réponse HTTP réussie et le JSON contractuel de santé exposé afin de détecter toute régression sur cette route."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "all good"}
