from fastapi import FastAPI
from app.routers import preferences

app = FastAPI(
    title="Notification Preferences API",
    description="Multi-tenant notification preferences management",
    version="1.0.0",
)

app.include_router(preferences.router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}
