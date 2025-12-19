from fastapi import FastAPI
from app.api import router as api_router
from app.utils.helpers import logger

app = FastAPI(
    title="AI Trading Signal Engine",
    description="Professional-grade AI engine for generating trading signals based on OHLCV data.",
    version="1.0.0"
)

app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    logger.info("AI Signal Engine starting up...")

@app.get("/")
def root():
    return {"message": "AI Signal Engine is running. Docs at /docs"}
