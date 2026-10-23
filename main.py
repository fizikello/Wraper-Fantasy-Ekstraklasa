
import logging

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from backend.database import get_db


logger = logging.getLogger(__name__)

app = FastAPI(
    title="Wraper Fantasy Analytics",
    description="Backend aplikacji Fantasy Ekstraklasa",
    version="0.2.0"
)


@app.get("/")
def home():
    return {
        "application": "Wraper Fantasy Analytics",
        "status": "running"
    }


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/db/status")
def database_status(db: Session = Depends(get_db)):
    try:
        result = db.execute(
            text("SELECT 1")
        ).scalar_one()

        return {
            "database": "connected",
            "test_result": result
        }

    except SQLAlchemyError:
        logger.exception("Database connection check failed")

        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        )


@app.get("/api/players")
def get_players(
    limit: int = Query(default=20, ge=1, le=100),
    name: str | None = Query(default=None, max_length=100),
    club: str | None = Query(default=None, max_length=100),
    position: str | None = Query(default=None, max_length=50),
    db: Session = Depends(get_db)
):
    query = text("""
        WITH latest_players AS (
            SELECT DISTINCT ON ("PLAYER_INDEX")
                "PLAYER_INDEX" AS player_id,
                "NAME" AS name,
                "CLUB" AS club,
                "POSITION" AS position,
                "PRICE" AS price,
                "POPULARITY" AS popularity,
                "SUM_POINTS" AS points_total,
                "DATE" AS updated_at
            FROM public.popularity
            WHERE "PLAYER_INDEX" IS NOT NULL
            ORDER BY
                "PLAYER_INDEX",
                "DATE" DESC NULLS LAST,
                "POPULARITY" DESC NULLS LAST,
                "PRICE" DESC NULLS LAST,
                "NAME" ASC NULLS LAST,
                "CLUB" ASC NULLS LAST
        )
        SELECT *
        FROM latest_players
        
        WHERE
            (CAST(:name AS TEXT) IS NULL
                OR name ILIKE '%' || CAST(:name AS TEXT) || '%')

            AND (CAST(:club AS TEXT) IS NULL
             OR club = CAST(:club AS TEXT))

            AND (CAST(:position AS TEXT) IS NULL
                OR position = CAST(:position AS TEXT))

        ORDER BY points_total DESC NULLS LAST, player_id
        LIMIT :limit
    """)

    result = db.execute(
        query,
        {
            "limit": limit,
            "name": name,
            "club": club,
            "position": position
        }
    )

    players = [dict(row) for row in result.mappings()]

    return {
        "count": len(players),
        "players": players
    }