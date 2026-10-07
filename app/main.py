from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import PROJECT_NAME, API_V1_STR, GENERATED_DIR
from app.core.database import engine, Base
from app.api.router import api_router

# Ensure tables are created
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure generated directory exists on startup
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title=PROJECT_NAME,
    description="Bulk Certificate Generator API for generating and retrieving course/event certificates at scale.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Enable CORS for local development / testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=API_V1_STR)


@app.get("/", tags=["Root"])
def root():
    return {
        "service": PROJECT_NAME,
        "status": "healthy",
        "docs_url": "/docs",
        "version": "1.0.0",
    }
