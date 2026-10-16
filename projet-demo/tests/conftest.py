from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers import items, reservations
from app.schemas.reservation import ReservationRead


@dataclass
class Storage:
    """Poignée de test sur les dictionnaires réellement utilisés par les routers."""

    items: dict[int, dict[str, Any]]
    reservations: dict[int, ReservationRead]

    def reset_all(self) -> None:
        """Vide les deux dictionnaires partagés."""
        self.items.clear()
        self.reservations.clear()


@pytest.fixture
def storage() -> Iterator[Storage]:
    """Réinitialise les stockages avant chaque test, fournit leur accès, puis les vide après l'exécution pour prévenir toute dépendance entre scénarios."""
    state = Storage(items=items.FAKE_DB, reservations=reservations.FAKE_DB)
    state.reset_all()
    yield state
    state.reset_all()


@pytest.fixture
def client(storage: Storage) -> TestClient:
    """Fournit le client HTTP en mémoire après avoir préparé un stockage propre."""
    return TestClient(app)


@pytest.fixture
def item_velo(client: TestClient) -> dict[str, Any]:
    """Crée un item réaliste par HTTP et le rend disponible aux tests dépendants, afin qu'ils partagent un contexte métier réutilisable."""
    response = client.post(
        "/items",
        json={
            "titre": "Vélo de ville",
            "description": "Trois vitesses",
            "tarif_jour": 8.5,
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def reservation_active(
    client: TestClient, item_velo: dict[str, Any]
) -> dict[str, Any]:
    """Prépare un contexte de réservation réutilisable en créant une réservation valide liée à un item par une requête HTTP réelle."""
    response = client.post(
        "/reservations",
        json={
            "item_id": item_velo["id"],
            "date_debut": "2026-09-01",
            "date_fin": "2026-09-05",
        },
    )
    assert response.status_code == 201
    return response.json()
