# Dockerfile

# pull the official docker image
FROM python:3.10-slim-bullseye

RUN apt-get update && apt-get install -y \
    build-essential libpq-dev libfreetype6-dev libpng-dev libjpeg-dev \
    libblas-dev liblapack-dev gfortran unzip \
    && rm -rf /var/lib/apt/lists/*

# set work directory
WORKDIR /api

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip install -r requirements.txt

# copy project
COPY . .

# Copy and set permissions for entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the port FastAPI will run on
EXPOSE 8000

# Use entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
# Command to run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]