FROM python:3.12-slim

WORKDIR /app

COPY ./src/log_processor /app/
RUN pip install --no-cache-dir -r requirements.txt

ARG WORKERS=4
ENV WORKERS=${WORKERS}

CMD ["python", "-m", "bytewax.run", "--workers", "$WORKERS", "main"]
