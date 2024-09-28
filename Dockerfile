FROM python:3.12-slim

WORKDIR /src/app

COPY requirements.txt /src/app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 80

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "80"]