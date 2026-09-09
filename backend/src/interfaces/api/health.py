from fastapi import APIRouter
from sqlalchemy import text

from src.infrastructure.db import engine


router = APIRouter()


@router.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "db": "ok",
        }

    except Exception:
        return {
            "status": "ok",
            "db": "error",
        }