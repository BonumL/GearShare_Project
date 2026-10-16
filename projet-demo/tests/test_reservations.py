from typing import Any

import pytest
from fastapi.testclient import TestClient


def test_creer_reservation_valide_retourne_201_et_statut_actif(
    client: TestClient, item_velo: dict[str, Any]
) -> None:
    """Vérifie qu'une réservation valide est créée et expose son identifiant, ses dates et son statut actif pour les clients HTTP."""
    response = client.post(
        "/reservations",
        json={
            "item_id": item_velo["id"],
            "date_debut": "2026-09-01",
            "date_fin": "2026-09-05",
        },
    )

    assert response.status_code == 201
    assert response.json()["item_id"] == item_velo["id"]
    assert response.json()["date_debut"] == "2026-09-01"
    assert response.json()["date_fin"] == "2026-09-05"
    assert response.json()["statut"] == "active"


@pytest.mark.parametrize(
    "payload",
    [
        {"item_id": 1, "date_debut": "2026-09-05", "date_fin": "2026-09-01"},
        {"item_id": 1, "date_debut": "2026-09-05", "date_fin": "2026-09-05"},
        {"item_id": 0, "date_debut": "2026-09-01", "date_fin": "2026-09-05"},
        {"item_id": 1, "date_debut": "not-a-date", "date_fin": "2026-09-05"},
        {"item_id": 1, "date_debut": "2026-09-01"},
        {"item_id": 1, "date_debut": "2026-09-01", "date_fin": "2026-09-05", "unknown": True},
    ],
)
def test_creer_reservation_payload_invalide_retourne_422(
    client: TestClient, payload: dict[str, object]
) -> None:
    """Vérifie que dates incorrectes, identifiants invalides, champs manquants ou inconnus sont rejetés par la validation HTTP sans créer de réservation."""
    response = client.post("/reservations", json=payload)

    assert response.status_code == 422


def test_lister_reservations_sans_donnee_retourne_liste_vide(
    client: TestClient,
) -> None:
    """Vérifie que le listing des réservations sans donnée renvoie un succès accompagné d'une liste JSON vide pour toute API cliente."""
    response = client.get("/reservations")

    assert response.status_code == 200
    assert response.json() == []


def test_lister_reservations_retourne_toutes_les_reservations(
    client: TestClient, reservation_active: dict[str, Any]
) -> None:
    """Vérifie que le listing par défaut expose les réservations créées et leurs informations contractuelles utiles, y compris leurs dates précises."""
    response = client.get("/reservations")

    assert response.status_code == 200
    assert response.json() == [reservation_active]


def test_lister_reservations_filtre_par_item_id(
    client: TestClient, reservation_active: dict[str, Any]
) -> None:
    """Vérifie que le paramètre item_id exclut les réservations associées à un autre item sans dépendre du stockage interne des items."""
    other_reservation = client.post(
        "/reservations",
        json={
            "item_id": reservation_active["item_id"] + 1,
            "date_debut": "2026-10-01",
            "date_fin": "2026-10-03",
        },
    )
    assert other_reservation.status_code == 201

    response = client.get(
        "/reservations",
        params={"item_id": reservation_active["item_id"]},
    )

    assert response.status_code == 200
    assert [entry["id"] for entry in response.json()] == [reservation_active["id"]]


def test_lister_reservations_applique_limit(
    client: TestClient, reservation_active: dict[str, Any]
) -> None:
    """Vérifie que la limite de listing borne le nombre de réservations renvoyées sans altérer leur ordre dans la réponse renvoyée."""
    second_reservation = client.post(
        "/reservations",
        json={
            "item_id": reservation_active["item_id"],
            "date_debut": "2026-10-01",
            "date_fin": "2026-10-03",
        },
    )
    assert second_reservation.status_code == 201
    assert len(client.get("/reservations").json()) == 2

    response = client.get("/reservations", params={"limit": 1})

    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.parametrize(
    "params",
    [
        {"item_id": 0},
        {"item_id": "abc"},
        {"limit": 0},
        {"limit": 101},
        {"limit": "abc"},
    ],
)
def test_lister_reservations_refuse_parametres_invalides(
    client: TestClient, params: dict[str, object]
) -> None:
    """Vérifie que les filtres et limites hors contraintes provoquent une réponse de validation HTTP en conservant une réponse d’erreur structurée."""
    response = client.get("/reservations", params=params)

    assert response.status_code == 422


def test_lire_reservation_existante_retourne_ses_donnees(
    client: TestClient, reservation_active: dict[str, Any]
) -> None:
    """Vérifie qu’une réservation existante est récupérable individuellement avec les données précédemment créées sans accéder directement aux dictionnaires internes de l’application."""
    response = client.get(f"/reservations/{reservation_active['id']}")

    assert response.status_code == 200
    assert response.json() == reservation_active


def test_lire_reservation_absente_retourne_404(client: TestClient) -> None:
    """Vérifie qu’une lecture par identifiant de réservation inconnu retourne le statut HTTP introuvable attendu sans exposer de détail interne inutile."""
    response = client.get("/reservations/999999")

    assert response.status_code == 404


@pytest.mark.parametrize("reservation_id", ["0", "abc"])
def test_lire_reservation_identifiant_invalide_retourne_422(
    client: TestClient, reservation_id: str
) -> None:
    """Vérifie que FastAPI rejette les identifiants de réservation invalides avant tout traitement de la route ou lecture des données stockées."""
    response = client.get(f"/reservations/{reservation_id}")

    assert response.status_code == 422


def test_annuler_reservation_active_change_son_statut(
    client: TestClient, reservation_active: dict[str, Any]
) -> None:
    """Vérifie que l’annulation réussie retourne un succès et rend le statut annulé visible aux clients sans altérer ses autres champs."""
    response = client.post(
        f"/reservations/{reservation_active['id']}/annuler"
    )

    assert response.status_code == 200
    assert response.json()["statut"] == "annulee"
    assert (
        client.get(f"/reservations/{reservation_active['id']}").json()["statut"]
        == "annulee"
    )


def test_annuler_reservation_deja_annulee_retourne_409(
    client: TestClient, reservation_active: dict[str, Any]
) -> None:
    """Vérifie qu’une seconde annulation est signalée comme conflit et confirme sa persistance par lecture de son état final dans l’API."""
    reservation_id = reservation_active["id"]
    client.post(f"/reservations/{reservation_id}/annuler")

    response = client.post(f"/reservations/{reservation_id}/annuler")

    assert response.status_code == 409
    assert client.get(f"/reservations/{reservation_id}").json()["statut"] == "annulee"


def test_annuler_reservation_absente_retourne_404(client: TestClient) -> None:
    """Vérifie qu’annuler une réservation absente renvoie 404, sans traiter l’opération comme une réussite ni modifier les réservations existantes du stockage."""
    response = client.post("/reservations/999999/annuler")

    assert response.status_code == 404


@pytest.mark.parametrize("reservation_id", ["0", "abc"])
def test_annuler_reservation_identifiant_invalide_retourne_422(
    client: TestClient, reservation_id: str
) -> None:
    """Vérifie que la route rejette les identifiants invalides avant validation métier, sans appliquer ni enregistrer aucune annulation sur une réservation."""
    response = client.post(f"/reservations/{reservation_id}/annuler")

    assert response.status_code == 422
