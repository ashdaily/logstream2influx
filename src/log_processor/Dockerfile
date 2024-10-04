FROM python:3.12-slim

WORKDIR /log_processor

COPY ./src/log_processor /log_processor/
RUN pip install --no-cache-dir -r requirements.txt

ARG WORKERS=4
ENV WORKERS=${WORKERS}

CMD ["python", "-m", "bytewax.run", "--workers", "$WORKERS", "main"]
