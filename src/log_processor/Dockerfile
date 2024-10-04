FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install bytewax-cli # can remove later

COPY . /app/

ARG WORKERS=4
ENV WORKERS=${WORKERS}

CMD ["python", "-m", "bytewax.run", "--workers", "$WORKERS", "main"]
