FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y \
    build-essential libpq-dev libfreetype6-dev libpng-dev libjpeg-dev \
    libblas-dev liblapack-dev gfortran \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /notebook

# Install base requirements (shared across all services)
COPY shared/requirements-base.txt /tmp/requirements-base.txt
RUN pip3 install --upgrade pip && \
    pip3 install -r /tmp/requirements-base.txt

# Install service-specific requirements
COPY notebook/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy the rest of the application code
COPY notebook/ .

# Expose port 8888 for Jupyter Notebook
EXPOSE 8888

# Command to run Jupyter Notebook
CMD ["bash", "-c", "jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --NotebookApp.token='' --NotebookApp.password=''"]
