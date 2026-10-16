from fastapi import FastAPI, Path, Query, HTTPException, Response
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate

from app.routers import items, reservations

app = FastAPI(title="GearShare API", version="0.1.0")
app.include_router(items.router)
app.include_router(reservations.router)

FAKE_DB: dict[int, dict] = {}

# ================ GET ================

@app.get("/health", tags=["monitoring"])
def health() -> dict[str, str]:
    return {"status": "all good"}

