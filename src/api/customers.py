from fastapi import APIRouter, HTTPException
from influx_client import InfluxClient
from models import CustomerStatsResponse

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/{customer_id}/stats", response_model=CustomerStatsResponse)
async def get_customer_stats_endpoint(customer_id: str, from_date: str):
    try:
        influx_client = InfluxClient()
        stats = influx_client.get_stats(customer_id, from_date)
        if not stats:
            raise HTTPException(status_code=404, detail="Customer data not found")

        response = CustomerStatsResponse(
            total_requests=stats["total_success"] + stats["total_failed"],
            successful_requests=stats["total_success"],
            failed_requests=stats["total_failed"],
            uptime=stats["uptime"],
            average_latency=stats["mean_latency"] or 0.0,
            median_latency=stats["median_latency"] or 0.0,
            p99_latency=stats["p99_latency"] or 0.0
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stats: {e}")
