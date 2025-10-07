from fastapi import FastAPI
from app.routers import organizations, documents, dashboard, assets, validation
app = FastAPI(title="Compliance Platform API - Example Implementation")

app.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
app.include_router(documents.router, prefix="/organizations/{orgId}/documents", tags=["Compliance Document"])
app.include_router(dashboard.router, prefix="", tags=["Dashboard"])
app.include_router(assets.router, prefix="/assets", tags=["Assets"])
app.include_router(validation.router, prefix="/validation", tags=["Validation"])
