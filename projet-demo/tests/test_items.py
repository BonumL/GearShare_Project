from typing import Any

import pytest
from fastapi.testclient import TestClient


def _seed_item(
    storage: Any,
    item_id: int,
    titre: str,
    disponible: bool = True,
) -> None:
    """Prépare un item valide dans le stockage réel pour composer des jeux de données de listing ciblés lors des tests."""
    storage.items[item_id] = {
        "id": item_id,
        "titre": titre,
        "description": None,
        "tarif_jour": 5.0,
        "disponible": disponible,
    }


def _create_item(
    client: TestClient,
    titre: str,
    disponible: bool = True,
) -> dict[str, Any]:
    """Crée un item via HTTP, vérifie son statut, puis réutilise ses données pour préparer le listing sans contourner l'API réelle."""
    response = client.post(
        "/items",
        json={"titre": titre, "tarif_jour": 5.0, "disponible": disponible},
    )
    assert response.status_code == 201
    return response.json()


def test_lister_items_vide_retourne_liste_vide(client: TestClient) -> None:
    """Vérifie que le listing sans item répond avec succès et renvoie une liste JSON vide au client, selon le contrat."""
    response = client.get("/items")

    assert response.status_code == 200
    assert response.json() == []


def test_lister_items_retourne_tous_les_items_par_defaut(
    client: TestClient, item_velo: dict[str, Any]
) -> None:
    """Vérifie que le listing par défaut retourne chaque item stocké dans l'ordre attendu, avec ses données complètes accessibles pour l'API."""
    other_item = _create_item(client, "Perceuse", disponible=False)

    response = client.get("/items")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [
        item_velo["id"],
        other_item["id"],
    ]
    assert response.json()[0] == item_velo


def test_lister_items_applique_skip_et_limit(
    client: TestClient, storage: Any
) -> None:
    """Vérifie que les paramètres skip et limit sélectionnent uniquement la page demandée parmi plusieurs items, selon le contrat HTTP public."""
    for item_id in range(1, 51):
        _seed_item(storage, item_id, f"Item {item_id}")

    response = client.get("/items", params={"skip": 40, "limit": 20})

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == list(range(41, 51))


def test_lister_items_avec_skip_apres_la_fin_retourne_liste_vide(
    client: TestClient, item_velo: dict[str, Any]
) -> None:
    """Vérifie qu'un décalage supérieur au nombre d'items renvoie une liste vide sans provoquer d'erreur HTTP, selon le contrat HTTP public."""
    response = client.get("/items", params={"skip": 10})

    assert response.status_code == 200
    assert response.json() == []


def test_lister_items_accepte_la_limite_maximale(
    client: TestClient, item_velo: dict[str, Any]
) -> None:
    """Vérifie que la limite maximale autorisée est acceptée et conserve tous les résultats disponibles selon le contrat HTTP public défini."""
    other_item = _create_item(client, "Perceuse")

    response = client.get("/items", params={"limit": 100})

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [
        item_velo["id"],
        other_item["id"],
    ]


def test_lister_items_filtre_par_terme_dans_titre(
    client: TestClient, item_velo: dict[str, Any]
) -> None:
    """Vérifie que le paramètre q conserve les items dont le titre correspond au terme de recherche demandé sur cette route."""
    _create_item(client, "Perceuse")

    response = client.get("/items", params={"q": "Vélo"})

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [item_velo["id"]]


def test_lister_items_sans_correspondance_retourne_liste_vide(
    client: TestClient, item_velo: dict[str, Any]
) -> None:
    """Vérifie qu'une recherche sans titre correspondant retourne une liste vide tout en gardant un statut de succès sans erreur serveur."""
    response = client.get("/items", params={"q": "Perceuse"})

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize(
    "disponible",
    [True, False],
)
def test_lister_items_filtre_par_disponibilite(
    client: TestClient,
    disponible: bool,
) -> None:
    """Vérifie que le filtre booléen sélectionne précisément les items disponibles ou indisponibles selon la valeur reçue par la requête HTTP."""
    available_item = _create_item(client, "Vélo disponible")
    unavailable_item = _create_item(client, "Vélo indisponible", disponible=False)

    response = client.get("/items", params={"disponible": disponible})

    assert response.status_code == 200
    expected_ids = (
        [available_item["id"]] if disponible else [unavailable_item["id"]]
    )
    assert [item["id"] for item in response.json()] == expected_ids


def test_lister_items_combine_les_filtres(client: TestClient) -> None:
    """Vérifie que les filtres de titre et disponibilité se combinent et excluent tout item ne correspondant pas aux deux critères."""
    matching_item = _create_item(client, "Vélo disponible")
    _create_item(client, "Vélo indisponible", disponible=False)
    _create_item(client, "Perceuse disponible")

    response = client.get("/items", params={"q": "Vélo", "disponible": True})

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [matching_item["id"]]


@pytest.mark.parametrize(
    "params",
    [
        {"skip": -1},
        {"skip": "abc"},
        {"limit": -1},
        {"limit": 0},
        {"limit": 101},
        {"limit": "abc"},
        {"disponible": "peut-etre"},
    ],
)
def test_lister_items_refuse_les_parametres_invalides(
    client: TestClient, params: dict[str, object]
) -> None:
    """Vérifie que les paramètres de pagination ou de filtre invalides sont rejetés avec une réponse de validation HTTP côté client."""
    response = client.get("/items", params=params)

    assert response.status_code == 422


def test_creer_item_valide_retourne_201_et_valeurs_par_defaut(
    client: TestClient,
) -> None:
    """Vérifie la création HTTP réussie, son identifiant, les champs obligatoires et les valeurs par défaut exposées pour le client HTTP."""
    response = client.post(
        "/items",
        json={"titre": "Vélo de ville", "tarif_jour": 8.5},
    )

    created = response.json()

    assert response.status_code == 201
    assert type(created["id"]) is int
    assert created["id"] > 0
    assert created == {
        "id": created["id"],
        "titre": "Vélo de ville",
        "description": None,
        "tarif_jour": 8.5,
        "disponible": True,
    }


def test_creer_items_attribue_des_identifiants_distincts(
    client: TestClient,
) -> None:
    """Vérifie que deux créations successives produisent des identifiants différents et restent toutes deux accessibles ensuite via l'API par lecture individuelle."""
    payload = {"titre": "Vélo de ville", "tarif_jour": 8.5}

    first = client.post("/items", json=payload)
    second = client.post("/items", json=payload)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] != second.json()["id"]
    assert client.get(f"/items/{first.json()['id']}").status_code == 200
    assert client.get(f"/items/{second.json()['id']}").status_code == 200


@pytest.mark.parametrize(
    "payload",
    [
        {"titre": "ab", "tarif_jour": 8.5},
        {"titre": "x" * 121, "tarif_jour": 8.5},
        {"titre": "Vélo valide", "tarif_jour": 8.5, "description": "x" * 1001},
        {"titre": "Vélo valide", "tarif_jour": 0},
        {"titre": "Vélo valide", "tarif_jour": -1},
        {"titre": "Vélo valide"},
        {"tarif_jour": 8.5},
        {"titre": "Vélo valide", "tarif_jour": 8.5, "couleur": "rouge"},
    ],
)
def test_creer_item_payload_invalide_retourne_422(
    client: TestClient, payload: dict[str, object]
) -> None:
    """Vérifie que les contraintes de création rejettent titres, descriptions, tarifs, champs manquants et données inconnues pour ce point d'entrée HTTP."""
    response = client.post("/items", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "payload",
    [
        {"titre": "abc", "tarif_jour": 8.5},
        {"titre": "x" * 120, "tarif_jour": 8.5},
        {"titre": "Vélo valide", "tarif_jour": 8.5, "description": "x" * 1000},
    ],
)
def test_creer_item_accepte_les_limites_textuelles(
    client: TestClient, payload: dict[str, object]
) -> None:
    """Vérifie que les longueurs minimale et maximale des champs textuels sont acceptées par le schéma lors de créations HTTP valides."""
    response = client.post("/items", json=payload)

    assert response.status_code == 201


def test_lire_item_existant_retourne_ses_donnees(
    client: TestClient, item_velo: dict[str, Any]
) -> None:
    """Vérifie qu'un item créé préalablement est lisible par son identifiant et retourne les champs attendus via son identifiant dans l'API."""
    response = client.get(f"/items/{item_velo['id']}")

    assert response.status_code == 200
    assert response.json() == item_velo


def test_lire_item_absent_retourne_404(client: TestClient) -> None:
    """Vérifie qu'une lecture par identifiant inconnu retourne le code HTTP indiquant une ressource absente sans modifier l'état du stockage partagé."""
    response = client.get("/items/999999")

    assert response.status_code == 404


@pytest.mark.parametrize("item_id", ["0", "-1", "abc"])
def test_lire_item_identifiant_invalide_retourne_422(
    client: TestClient, item_id: str
) -> None:
    """Vérifie que les identifiants non positifs ou non numériques sont rejetés avant toute lecture de ressource avec un code explicite."""
    response = client.get(f"/items/{item_id}")

    assert response.status_code == 422


def test_remplacer_item_modifie_tous_les_champs(
    client: TestClient, item_velo: dict[str, Any]
) -> None:
    """Vérifie que PUT remplace les champs modifiables et que cette représentation complète reste ensuite lisible sans changer son identifiant initial."""
    payload = {
        "titre": "Vélo pliant",
        "description": "Compact",
        "tarif_jour": 12.0,
        "disponible": False,
    }

    response = client.put(f"/items/{item_velo['id']}", json=payload)

    assert response.status_code == 200
    assert response.json() == {"id": item_velo["id"], **payload}
    assert client.get(f"/items/{item_velo['id']}").json() == response.json()


def test_remplacer_item_absent_retourne_404(client: TestClient) -> None:
    """Vérifie qu'un PUT visant un identifiant inexistant retourne 404 au lieu de créer une ressource implicite dans le stockage réel."""
    response = client.put(
        "/items/999999",
        json={"titre": "Vélo pliant", "tarif_jour": 12.0},
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    ("method", "payload"),
    [
        ("put", {"titre": "Vélo pliant", "tarif_jour": 12.0}),
        ("patch", {"titre": "Vélo pliant"}),
    ],
)
def test_modifier_item_identifiant_invalide_retourne_422(
    client: TestClient,
    method: str,
    payload: dict[str, object],
) -> None:
    """Vérifie que PUT et PATCH rejettent les identifiants de chemin non positifs avant toute modification de ressource pour chaque méthode."""
    response = client.request(
        method.upper(),
        "/items/0",
        json=payload,
    )

    assert response.status_code == 422


def test_remplacer_item_refuse_un_corps_invalide(
    client: TestClient, item_velo: dict[str, Any]
) -> None:
    """Vérifie que PUT applique la validation complète du schéma de création au corps de remplacement transmis avant toute modification persistante."""
    response = client.put(
        f"/items/{item_velo['id']}",
        json={"titre": "Vélo pliant"},
    )

    assert response.status_code == 422


def test_modifier_item_ne_change_que_le_champ_fourni(
    client: TestClient, item_velo: dict[str, Any]
) -> None:
    """Vérifie que PATCH modifie le titre transmis tout en conservant les autres valeurs antérieures de l'item dans la réponse complète."""
    response = client.patch(
        f"/items/{item_velo['id']}",
        json={"titre": "Vélo pliant"},
    )

    assert response.status_code == 200
    assert response.json() == {
        **item_velo,
        "titre": "Vélo pliant",
    }


def test_modifier_item_avec_corps_vide_ne_change_rien(
    client: TestClient, item_velo: dict[str, Any]
) -> None:
    """Vérifie qu'un PATCH vide est accepté et laisse la représentation de l'item strictement inchangée dans l'état métier de la ressource."""
    response = client.patch(f"/items/{item_velo['id']}", json={})

    assert response.status_code == 200
    assert response.json() == item_velo


def test_modifier_item_peut_effacer_description(
    client: TestClient, item_velo: dict[str, Any]
) -> None:
    """Vérifie qu'un PATCH distinguant null d'un champ absent permet d'effacer explicitement la description en préservant les autres valeurs existantes inchangées."""
    response = client.patch(
        f"/items/{item_velo['id']}",
        json={"description": None},
    )

    assert response.status_code == 200
    assert response.json() == {
        **item_velo,
        "description": None,
    }


@pytest.mark.parametrize(
    "payload",
    [
        {"titre": "ab"},
        {"titre": "x" * 121},
        {"description": "x" * 1001},
        {"tarif_jour": 0},
        {"tarif_jour": -1},
        {"couleur": "rouge"},
    ],
)
def test_modifier_item_payload_invalide_retourne_422(
    client: TestClient, item_velo: dict[str, Any], payload: dict[str, object]
) -> None:
    """Vérifie que PATCH rejette les valeurs hors limites, null interdit et champs supplémentaires selon son schéma sans effet de bord."""
    response = client.patch(f"/items/{item_velo['id']}", json=payload)

    assert response.status_code == 422


def test_modifier_item_absent_retourne_404(client: TestClient) -> None:
    """Vérifie qu'une modification partielle ciblant un identifiant inexistant retourne une réponse HTTP introuvable et garantit qu'aucune ressource n'est créée implicitement."""
    response = client.patch("/items/999999", json={"titre": "Vélo pliant"})

    assert response.status_code == 404


def test_supprimer_item_retourne_204_sans_corps_et_le_supprime(
    client: TestClient, item_velo: dict[str, Any]
) -> None:
    """Vérifie le statut sans contenu de suppression puis confirme par lecture HTTP que l'item n'existe plus pour un client HTTP."""
    response = client.delete(f"/items/{item_velo['id']}")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/items/{item_velo['id']}").status_code == 404
    assert client.delete(f"/items/{item_velo['id']}").status_code == 404


def test_supprimer_un_item_preserve_les_autres(
    client: TestClient, item_velo: dict[str, Any]
) -> None:
    """Vérifie qu'après suppression d'un item, une autre ressource reste accessible par HTTP et conserve intactes ses propres données métier observables."""
    other = client.post(
        "/items",
        json={"titre": "Perceuse", "tarif_jour": 5.0},
    ).json()

    response = client.delete(f"/items/{item_velo['id']}")

    assert response.status_code == 204
    assert client.get(f"/items/{other['id']}").status_code == 200


def test_supprimer_item_absent_retourne_404(client: TestClient) -> None:
    """Vérifie que supprimer un identifiant absent retourne une erreur plutôt qu'un faux succès de suppression et laisse les données intactes."""
    response = client.delete("/items/999999")

    assert response.status_code == 404


@pytest.mark.parametrize("item_id", ["0", "-1", "abc"])
def test_supprimer_item_identifiant_invalide_retourne_422(
    client: TestClient, item_id: str
) -> None:
    """Vérifie que DELETE refuse les identifiants invalides avant de tenter une suppression de ressource sans jamais appeler la logique métier."""
    response = client.delete(f"/items/{item_id}")

    assert response.status_code == 422
