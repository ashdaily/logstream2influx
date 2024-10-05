FROM python:3.12-slim

WORKDIR /log_generator
COPY src/log_generator/log_generator.py /log_generator/
COPY .env.local /log_generator/
COPY ./wait-for-it.sh /log_generator

RUN pip install --no-cache-dir python-dotenv

WORKDIR /log_generator

# Set the entrypoint to wait for log_processor before starting log_generator.py
ENTRYPOINT ["./wait-for-it.sh", "log_processor:8086", "--timeout=60", "--", "python", "log_generator.py"]