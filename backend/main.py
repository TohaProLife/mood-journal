from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import engine, Base
from routers.entries import router as entries_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mood Journal API")

app.include_router(entries_router)
app.mount("/static", StaticFiles(directory="../frontend"), name="static")


@app.get("/")
def index():
    return FileResponse("../frontend/index.html")
