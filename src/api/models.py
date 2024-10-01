from pydantic import BaseModel


class CustomerStatsResponse(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    uptime: float
    average_latency: float
    median_latency: float
    p99_latency: float
