from pydantic import EmailStr
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date, timedelta, date
from fastapi import Body


class SegmentationInput(BaseModel):
    dataset: str
    text: str


class SegmentationResponse(BaseModel):
    processed_date: datetime
    processed_type: str
    passages: List[str]
