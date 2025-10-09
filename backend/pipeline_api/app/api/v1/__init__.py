from fastapi import APIRouter

from app.api.v1 import entries
from app.api.v1 import reports  # ensure you have app/api/v1/reports.py present

api_router = APIRouter()
api_router.include_router(entries.router)
api_router.include_router(reports.router)
