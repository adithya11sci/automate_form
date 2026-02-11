# Use official Python 3.9 lightweight image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for Playwright and Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libgconf-2-4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libgbm-dev \
    libnss3-dev \
    libxss-dev \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY backend/requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright Browsers (Chromium)
RUN playwright install --with-deps chromium

# Copy the rest of the application
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY api/ ./api/
COPY .env .

# Set environment variables
ENV PYTHONPATH=/app
ENV HEADLESS=true
ENV PYTHONUNBUFFERED=1

# Make the script executable
RUN chmod +x start_app.sh

# Expose the default port (Render will override this)
EXPOSE 7860

# Run the startup script
CMD ["/bin/bash", "./start_app.sh"]

