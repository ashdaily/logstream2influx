import logging
from datetime import datetime

from fastapi import Query
from fastapi import APIRouter, HTTPException
from influx_client import InfluxClient

from models import CustomerStatsResponse

logger = logging.getLogger("customer_stats")
logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler('customer_stats.log'),
                logging.StreamHandler()
            ]
        )

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/{customer_id}/stats", response_model=CustomerStatsResponse)
async def get_customer_stats_endpoint(customer_id: str, from_date: str = Query(...)):
    try:
        datetime.strptime(from_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid date format, expected YYYY-MM-DD")

    logger.info(f"Received request for customer stats: customer_id={customer_id}, from_date={from_date}")
    try:
        with InfluxClient() as influx_client:
            stats = influx_client.get_stats(customer_id, from_date)
            if not stats:
                logger.warning(f"No stats found for customer_id={customer_id}, from_date={from_date}")
                raise HTTPException(status_code=404, detail="Customer data not found")
            logger.info(f"Returning stats for customer_id={customer_id}, from_date={from_date}")
            return stats
    except Exception as e:
        logger.error(f"Error while retrieving stats for customer_id={customer_id}, from_date={from_date}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stats: {e}")
