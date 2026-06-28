# Use Python 3.10-slim as the base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for psycopg2-binary and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies without caching to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY api.py .
COPY core_logic.py .
COPY db_utils.py .
COPY llm_config.py .
COPY main.py .
COPY rag_agent.py .
COPY sql_agent.py .
COPY streamlit_app.py .

# Copy data directory
COPY data/ ./data/

# Set default environment variables (can be overridden at runtime)
ENV API_URL=http://localhost:8000
ENV PYTHONUNBUFFERED=1

# Expose ports
# Port 8000 for FastAPI backend
# Port 8501 for Streamlit frontend
EXPOSE 8000 8501

# Health check for the API endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/docs')" || exit 1

# Start the application
CMD ["python", "main.py"]
