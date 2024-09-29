FROM python:3.12-slim

WORKDIR /src/app

COPY src/app/requirements.txt /src/app/requirements.txt
COPY src/config /src/app/

RUN pip install --no-cache-dir -r requirements.txt

COPY ../.. .
EXPOSE 80

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "80"]