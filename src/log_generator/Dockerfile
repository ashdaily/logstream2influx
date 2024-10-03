FROM python:3.12-slim

WORKDIR /log_generator
COPY src/log_generator/log_generator.py /log_generator/
COPY .env.local /log_generator/
RUN pip install --no-cache-dir python-dotenv
CMD ["python", "/log_generator/log_generator.py"]