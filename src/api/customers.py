from fastapi import APIRouter, HTTPException, Depends
from influx_client import InfluxClient
from models import CustomerStatsResponse
from validators import CustomerStatsRequest
import logging

logger = logging.getLogger("customer_stats")
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('customer_stats.log'),
        logging.StreamHandler()
    ]
)

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/{customer_id}/stats", response_model=CustomerStatsResponse)
async def get_customer_stats_endpoint(
        customer_id: str,
        request: CustomerStatsRequest = Depends()
):
    validated_date = request.from_date

    logger.info(f"Received request for customer stats: customer_id={customer_id}, from_date={validated_date}")

    try:
        with InfluxClient() as influx_client:
            stats = influx_client.get_stats(customer_id, validated_date)
            if not stats:
                logger.warning(f"No stats found for customer_id={customer_id}, from_date={validated_date}")
                raise HTTPException(status_code=404, detail="Customer data not found")
            logger.info(f"Returning stats for customer_id={customer_id}, from_date={validated_date}")
            return stats
    except Exception as e:
        logger.error(f"Error while retrieving stats for customer_id={customer_id}, from_date={validated_date}: {e}")
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=f"Failed to retrieve stats: {e}")


@router.get("/customer/stats/all", response_model=CustomerStatsResponse)
async def get_all_stats_endpoint(
        request: CustomerStatsRequest = Depends()
):
    validated_date = request.from_date

    logger.info(f"Received request for all customer stats: from_date={validated_date}")

    try:
        with InfluxClient() as influx_client:
            stats = influx_client.get_all_stats(validated_date)
            if not stats:
                logger.warning(f"No stats found from_date={validated_date}")
                raise HTTPException(status_code=404, detail="Customer data not found")
            logger.info(f"Returning stats for all customers, from_date={validated_date}")
            return stats
    except Exception as e:
        logger.error(f"Error while retrieving stats for all customers, from_date={validated_date}: {e}")
        raise HTTPException(status_code=getattr(e, "status_code", 500), detail=f"Failed to retrieve stats: {e}")
