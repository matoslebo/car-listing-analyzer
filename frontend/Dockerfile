FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for Docker layer caching
COPY requirements.txt .

# Install only what frontend needs (NOT chromadb, langchain, etc.)
RUN pip install --no-cache-dir streamlit requests

# Copy frontend code
COPY frontend/ ./frontend/

# Streamlit defaults to port 8501
EXPOSE 8501

# Run streamlit
CMD ["streamlit", "run", "frontend/streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]