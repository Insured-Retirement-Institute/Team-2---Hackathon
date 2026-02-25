import asyncio
import logging
import os
from typing import Annotated, AsyncGenerator

import asyncpg
from asyncpg import Connection
from fastapi import Depends, HTTPException

from api.config import QUERIES_DIR

logger = logging.getLogger(__name__)

pool: asyncpg.Pool | None = None
queries: dict[str, str] = {}


def load_queries() -> dict[str, str]:
    return {f.stem: f.read_text() for f in QUERIES_DIR.glob("*.sql")}


async def init_db(max_retries: int = 3, retry_delay: float = 2.0):
    global pool, queries

    queries = load_queries()
    logger.info(f"Loaded {len(queries)} SQL queries: {list(queries.keys())}")

    pghost = os.environ.get("PGHOST", "localhost")
    pgport = os.environ.get("PGPORT", "5432")
    pgdatabase = os.environ.get("PGDATABASE", "postgres")
    logger.info(f"Connecting to {pghost}:{pgport}/{pgdatabase}")

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Connection attempt {attempt}/{max_retries}...")
            pool = await asyncpg.create_pool(
                min_size=1,
                max_size=10,
                command_timeout=30,
                timeout=10,
            )
            logger.info("Database connection pool created successfully")
            return
        except TimeoutError:
            logger.error(f"Attempt {attempt}: Connection timed out after 10 seconds")
        except OSError as e:
            logger.error(f"Attempt {attempt}: Network error: {e}")
        except asyncpg.InvalidPasswordError:
            logger.error("Invalid database password")
            raise
        except asyncpg.InvalidCatalogNameError as e:
            logger.error(f"Database does not exist: {e}")
            raise
        except Exception as e:
            logger.error(f"Attempt {attempt}: Unexpected error: {type(e).__name__}: {e}")

        if attempt < max_retries:
            logger.info(f"Retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)
            retry_delay *= 2

    raise RuntimeError(f"Failed to connect to database after {max_retries} attempts")


async def close_db():
    if pool:
        await pool.close()


async def get_db() -> AsyncGenerator[Connection, None]:
    global pool
    if pool is None or pool._closed:
        raise HTTPException(status_code=503, detail="Database not available")
    async with pool.acquire() as conn:
        yield conn


DbConnection = Annotated[Connection, Depends(get_db)]


async def fetch_rows(conn: Connection, query_name: str, *args) -> list[dict]:
    sql = queries.get(query_name)
    if sql is None:
        raise HTTPException(status_code=500, detail=f"Query {query_name} not found")
    rows = await conn.fetch(sql, *args)
    return [dict(r) for r in rows]
