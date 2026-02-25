import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api import database
from api.database import close_db, init_db
<<<<<<< Updated upstream
from api.routers import passthrough, policies, profiles, alerts, responsible_ai
=======
from api.routers import passthrough, policies, profiles, alerts, compare, actions, products, responsible_ai
>>>>>>> Stashed changes

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Starting application...")
    await init_db()
    logger.info("Application startup complete")
    yield
    logger.info("Shutting down application...")
    await close_db()
    logger.info("Application shutdown complete")


root_path = os.environ.get("ROOT_PATH", "")
app = FastAPI(
    lifespan=lifespan,
    root_path=root_path,
    swagger_ui_parameters={"url": f"{root_path}/openapi.json"} if root_path else None,
)


@app.get("/health")
async def health():
    db_status = "connected" if database.pool and not database.pool._closed else "disconnected"
    return {"status": "ok", "database": db_status}


@app.get("/health/ready")
async def readiness():
    if not database.pool or database.pool._closed:
        return {"status": "not_ready", "reason": "database not connected"}
    try:
        async with database.pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "reason": str(e)}

app.include_router(passthrough.router)
app.include_router(policies.router)
app.include_router(alerts.router)
app.include_router(profiles.router)
<<<<<<< Updated upstream
=======
app.include_router(compare.router)
app.include_router(actions.router)
app.include_router(products.router)
>>>>>>> Stashed changes
app.include_router(responsible_ai.router)
