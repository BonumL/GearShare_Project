from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.item import ItemUpdate
from app.schemas.reservation import ReservationCreate


def test_item_update_sans_champ_ne_modifie_aucune_valeur() -> None:
    """Vérifie qu'un schéma PATCH vide distingue les champs absents et produit un dictionnaire de modification vide sans requête HTTP directe."""
    assert ItemUpdate().model_dump(exclude_unset=True) == {}


def test_reservation_valide_est_acceptee_par_le_schema() -> None:
    """Vérifie l'acceptation d'une période dont la fin est strictement postérieure au début, conformément aux contraintes métier du schéma Pydantic ReservationCreate."""
    reservation = ReservationCreate(
        item_id=1,
        date_debut=date(2026, 9, 1),
        date_fin=date(2026, 9, 5),
    )

    assert reservation.date_fin > reservation.date_debut


@pytest.mark.parametrize(
    ("date_debut", "date_fin"),
    [
        (date(2026, 9, 5), date(2026, 9, 1)),
        (date(2026, 9, 5), date(2026, 9, 5)),
    ],
)
def test_periode_invalide_est_refusee_par_le_schema(
    date_debut: date, date_fin: date
) -> None:
    """Vérifie le rejet des périodes inversées ou nulles par Pydantic, sans client HTTP lors d'un test ciblant la règle métier."""
    with pytest.raises(ValidationError, match="date_fin"):
        ReservationCreate(
            item_id=1,
            date_debut=date_debut,
            date_fin=date_fin,
        )
