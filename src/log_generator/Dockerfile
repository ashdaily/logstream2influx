FROM python:3.12-slim

WORKDIR /log_generator
COPY src/log_generator/log_generator.py .
COPY src/config/ /log_generator/config/
RUN pip install --no-cache-dir python-dotenv
CMD ["python", "log_generator.py"]