import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import admin, auth, news, profile
from app.core.config import settings
from app.db.session import SessionLocal
from app.services.audit import write_log
from app.services.seed import seed_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(title=settings.project_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(news.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.on_event("startup")
def on_startup() -> None:
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    db = SessionLocal()
    try:
        write_log(
            db,
            action="server_error",
            entity="server",
            level="error",
            message=str(exc),
            ip_address=request.client.host if request.client else None,
        )
    finally:
        db.close()
    return JSONResponse(status_code=500, content={"detail": "Внутренняя ошибка сервера"})


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
