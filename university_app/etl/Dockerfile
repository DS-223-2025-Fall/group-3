FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y \
    build-essential libpq-dev libfreetype6-dev libpng-dev libjpeg-dev \
    libblas-dev liblapack-dev gfortran \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /etl

# Copy requirements file and install dependencies
COPY requirements.txt . 
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Make the ETL runner script executable
RUN chmod +x run_etl.sh

# Expose port 3000
EXPOSE 3000

# Command to run the complete ETL process (generate data + create tables + load data)
# Use bash explicitly to avoid permission issues with volume mounts
# COMMENTED OUT: ETL no longer runs automatically to prevent data regeneration
# To run ETL manually: docker compose run --rm etl bash run_etl.sh
# CMD ["bash", "run_etl.sh"]

# Keep container running but don't execute ETL automatically
CMD ["tail", "-f", "/dev/null"]