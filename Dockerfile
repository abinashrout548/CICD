FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY etl_script.py .
COPY data.csv .

# Environment variables (override when running container)
ENV CSV_FILE=data.csv
ENV DB_HOST=host.docker.internal
ENV DB_PORT=3306
ENV DB_NAME=etl_db
ENV DB_USER=root
ENV DB_PASS=password
ENV TABLE_NAME=etl_output

CMD ["python", "etl_script.py"]
