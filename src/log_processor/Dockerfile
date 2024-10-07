FROM python:3.12-slim

WORKDIR /log_processor

COPY ./src/log_processor /log_processor/

RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

#ARG WORKERS=4
#ENV WORKERS=${WORKERS}

CMD sh -c "python -m bytewax.run main"