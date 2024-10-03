from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator
from fastapi import HTTPException


class CustomerStatsRequest(BaseModel):
    from_date: str = Field(..., description="Date from which to fetch stats, in YYYY-MM-DD format")

    @field_validator("from_date")
    def validate_from_date(cls, v):
        try:
            parsed_date = datetime.strptime(v, "%Y-%m-%d").date()
            if parsed_date > date.today():
                raise ValueError("Date cannot be in the future.")
            return v
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid date format, expected YYYY-MM-DD")
