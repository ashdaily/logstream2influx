FROM python:3.12-slim

WORKDIR /log_processor

COPY src/log_processor/ /log_processor/

COPY src/log_processor/requirements.txt /log_processor/
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8086

CMD ["python", "-m", "bytewax.run", "main"]