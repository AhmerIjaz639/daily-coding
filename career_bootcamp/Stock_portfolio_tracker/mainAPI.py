from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime,date
from typing import Optional
from databse import get_db

app=FastAPI(
    title="Finance Tracker API",
    version="0.1.0",
    description="API for tracking stocks and portfolio"
)

