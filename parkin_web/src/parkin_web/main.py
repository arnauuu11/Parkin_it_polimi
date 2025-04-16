# src/parkin_web/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os

from src.parkin_web.core.config import settings
from src.parkin_web.api.routes import auth, parking, bookings, users, payments, web
from src.parkin_web.db.session import engine
from src.parkin_web.db.base import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the root directory of the project
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(ROOT_DIR, "static")), name="static")

# Include API routes
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(parking.router, prefix=settings.API_V1_STR)
app.include_router(bookings.router, prefix=settings.API_V1_STR)
app.include_router(payments.router, prefix=settings.API_V1_STR)

# Set up templates
templates = Jinja2Templates(directory=os.path.join(ROOT_DIR, "templates"))

# Include web routes for rendering templates
app.include_router(web.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.parkin_web.main:app", host="0.0.0.0", port=8000, reload=True)