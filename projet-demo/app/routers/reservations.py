from fastapi import APIRouter, HTTPException, Path, Query

from app.schemas.reservation import ReservationCreate, ReservationRead

router = APIRouter(prefix="/reservations", tags=["reservations"])

FAKE_DB: dict[int, ReservationRead] = {}
_next_id = 1


@router.post("", response_model=ReservationRead, status_code=201)
def create_reservation(payload: ReservationCreate) -> ReservationRead:
    global _next_id
    reservation = ReservationRead(
        id=_next_id,
        **payload.model_dump(),
        statut="active",
    )
    FAKE_DB[_next_id] = reservation
    _next_id += 1
    return reservation


@router.get("", response_model=list[ReservationRead], status_code=200)
def list_reservations(
    item_id: int | None = Query(default=None, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[ReservationRead]:
    reservations = list(FAKE_DB.values())
    if item_id is not None:
        reservations = [
            reservation
            for reservation in reservations
            if reservation.item_id == item_id
        ]
    return reservations[:limit]


@router.get(
    "/{reservation_id}",
    response_model=ReservationRead,
    status_code=200,
)
def get_reservation(
    reservation_id: int = Path(ge=1),
) -> ReservationRead:
    reservation = FAKE_DB.get(reservation_id)
    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail=f"Réservation {reservation_id} introuvable.",
        )
    return reservation


@router.post(
    "/{reservation_id}/annuler",
    response_model=ReservationRead,
    status_code=200,
)
def cancel_reservation(
    reservation_id: int = Path(ge=1),
) -> ReservationRead:
    reservation = FAKE_DB.get(reservation_id)
    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail=f"Réservation {reservation_id} introuvable.",
        )
    if reservation.statut == "annulee":
        raise HTTPException(
            status_code=409,
            detail=f"Réservation {reservation_id} déjà annulée.",
        )

    cancelled_reservation = reservation.model_copy(update={"statut": "annulee"})
    FAKE_DB[reservation_id] = cancelled_reservation
    return cancelled_reservation
