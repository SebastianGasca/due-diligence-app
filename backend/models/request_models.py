# backend/models/request_models.py

from pydantic import BaseModel
from datetime import date
from typing import List

class NewsRequest(BaseModel):
    company: str
    start_date: date
    end_date: date
    keywords: List[str]