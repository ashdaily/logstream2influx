from pydantic import BaseModel, Field
from typing import Optional


class CustomerStatsResponse(BaseModel):
    total_requests: Optional[int] = Field(None, description="Total number of requests")
    successful_requests: Optional[int] = Field(None, description="Total number of successful requests")
    failed_requests: Optional[int] = Field(None, description="Total number of failed requests")
    uptime: Optional[float] = Field(None, description="Uptime percentage")
    average_latency: Optional[float] = Field(None, description="Average latency in seconds")
    median_latency: Optional[float] = Field(None, description="Median latency in seconds")
    p99_latency: Optional[float] = Field(None, description="99th percentile latency in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "total_requests": 100,
                "successful_requests": 90,
                "failed_requests": 10,
                "uptime": 90.0,
                "average_latency": 0.5,
                "median_latency": 0.4,
                "p99_latency": 0.8
            }
        }

