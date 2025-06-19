FROM python:3.10-slim

WORKDIR /app

COPY ./smart-dashboard-poc /app

# Install system dependencies including those needed for Playwright
RUN apt-get update && \
    apt-get install -y \
    gcc \
    curl \
    build-essential \
    # Playwright dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && playwright install --with-deps chromium \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set display environment variable for Playwright
ENV DISPLAY=:99

CMD ["python", "-m", "workers.worker"]
