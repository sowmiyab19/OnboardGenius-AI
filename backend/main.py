import logging
import os

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError

from backend.database.database import engine, Base
from backend.routers import (
    auth,
    users,
    employees,
    tasks,
    documents,
    announcements,
    chat,
)

# ----------------------------
# 1. Logging Setup
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("backend.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger("OnboardGenius")


# ----------------------------
# 2. Create FastAPI app FIRST
# ----------------------------
app = FastAPI(
    title="OnboardGenius AI API",
    description="Backend API for onboarding system",
    version="1.0.0",
)


# ----------------------------
# 3. CORS Setup
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# 4. Safe Database Initialization
# ----------------------------
@app.on_event("startup")
def startup():
    try:
        logger.info("Initializing database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully!")
    except Exception as e:
        logger.error(f"DB init failed: {e}", exc_info=True)


# ----------------------------
# 5. Exception Handlers
# ----------------------------
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error occurred"},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# ----------------------------
# 6. Routers
# ----------------------------
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(employees.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(announcements.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


# ----------------------------
# 7. Safe Static Files Mount
# ----------------------------
FRONTEND_DIR = "frontend"

if os.path.exists(FRONTEND_DIR):
    app.mount(
        "/frontend",
        StaticFiles(directory=FRONTEND_DIR, html=True),
        name="frontend",
    )
    logger.info("Frontend mounted successfully.")
else:
    logger.warning("Frontend folder not found. Skipping static file mount.")


# ----------------------------
# 8. Health Check Route (IMPORTANT)
# ----------------------------
@app.get("/")
def root():
    return {"status": "OnboardGenius API is running 🚀"}