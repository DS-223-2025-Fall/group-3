FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y \
    build-essential libpq-dev libfreetype6-dev libpng-dev libjpeg-dev \
    libblas-dev liblapack-dev gfortran unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /api

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install base requirements (shared across all services)
COPY shared/requirements-base.txt /tmp/requirements-base.txt
RUN pip3 install --upgrade pip && \
    pip install -r /tmp/requirements-base.txt

# Install service-specific requirements
COPY api/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY api/ .
COPY api/entrypoint.sh /docker-entrypoint.sh
RUN sed -i 's/\r$//' /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]