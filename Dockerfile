# Use official Python 3.12 image
FROM python:3.12-slim

# Install system deps for audio processing and C/C++ extensions
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      ffmpeg \
      rubberband-cli \
      build-essential \
      libsndfile1 \
      git \
    && rm -rf /var/lib/apt/lists/*

# Set working dir
WORKDIR /mashupAPI

# Copy and install Python build tools + requirements
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel cython numpy \
 && pip install --no-cache-dir --no-build-isolation -r requirements.txt

# Copy application code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Launch Uvicorn on container start
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]