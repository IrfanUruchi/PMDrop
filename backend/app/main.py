from fastapi import FastAPI
from app.routes.stats import router as stats_router
from fastapi.staticfiles import StaticFiles
from app.routes import signaling

from app.routes.files import router as files_router
from app.routes.devices import router as devices_router
from app.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PMDrop")

app.include_router(files_router)
app.include_router(devices_router)
app.include_router(stats_router)

app.include_router(signaling.router)

app.mount(
    "/",
    StaticFiles(directory="../frontend/static", html=True),
    name="static"
)
