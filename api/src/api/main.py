from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.database import close_db, init_db
from api.routers import passthrough, policies


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(lifespan=lifespan)

app.include_router(passthrough.router)
app.include_router(policies.router)
