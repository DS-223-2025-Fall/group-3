FROM python:3.10-slim-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /docs

# Install MkDocs and dependencies
RUN pip3 install --upgrade pip && \
    pip3 install mkdocs==1.6.1 mkdocs-material==9.5.50 "mkdocstrings[python]==0.25.1"

# Copy documentation files
COPY mkdocs.yaml /docs/
COPY docs/ /docs/docs/

# Expose port for MkDocs server
EXPOSE 8000

# Run MkDocs serve
CMD ["mkdocs", "serve", "--dev-addr=0.0.0.0:8000"]

