from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
import logging
from app.routers.expense import router as expenses_router
from app.core.database import get_db



app= FastAPI()
app.include_router(expenses_router)
logger = logging.getLogger("uvicorn.error")


@app.get("/")
def root():
    return {
        "message":"THis is the starting page"
        
    }


@app.get("/health/db")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "Connected"}
    except Exception as e:
        logger.exception("DB health check failed")
        raise HTTPException(status_code=500, detail=f"Database Unavailable: {e}")     