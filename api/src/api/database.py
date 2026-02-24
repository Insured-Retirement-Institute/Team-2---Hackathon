import asyncpg
from fastapi import HTTPException

from api.config import DATABASE_URL, QUERIES_DIR

pool: asyncpg.Pool | None = None
queries: dict[str, str] = {}


def load_queries() -> dict[str, str]:
    return {f.stem: f.read_text() for f in QUERIES_DIR.glob("*.sql")}


async def init_db():
    global pool, queries
    queries = load_queries()
    pool = await asyncpg.create_pool(DATABASE_URL)


async def close_db():
    if pool:
        await pool.close()


async def fetch_rows(query_name: str, *args) -> list[dict]:
    sql = queries.get(query_name)
    if sql is None:
        raise HTTPException(status_code=500, detail=f"Query {query_name} not found")
    rows = await pool.fetch(sql, *args)
    return [dict(r) for r in rows]
