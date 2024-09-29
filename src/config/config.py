import os
from dotenv import load_dotenv


load_dotenv('.env.local')  # FIXME: pass filename as env var


class Config:
    @staticmethod
    def get_influx_db_url() -> str:
        return os.getenv('INFLUXDB_URL')

    @staticmethod
    def get_influx_org_name() -> str:
        return os.getenv('DOCKER_INFLUXDB_INIT_ORG')

    @staticmethod
    def get_influx_bucket_name() -> str:
        return os.getenv('DOCKER_INFLUXDB_INIT_BUCKET')

    @staticmethod
    def get_log_generator_batch_size() -> int:
        return int(os.getenv('LOG_BATCH_SIZE'))

    @staticmethod
    def get_log_generator_interval_seconds() -> int:
        return int(os.getenv('LOG_INTERVAL_SECONDS'))

    @staticmethod
    def get_log_generator_log_file_path() -> str:
        return os.getenv('LOG_FILE_PATH', 'api_requests.log')
