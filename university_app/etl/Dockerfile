FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y \
    build-essential libpq-dev libfreetype6-dev libpng-dev libjpeg-dev \
    libblas-dev liblapack-dev gfortran \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /etl

COPY requirements.txt . 
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

COPY . .

RUN chmod +x run_etl.sh

EXPOSE 3000

# ETL runs manually: docker compose run --rm etl bash run_etl.sh
CMD ["tail", "-f", "/dev/null"]