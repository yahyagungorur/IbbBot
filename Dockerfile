FROM python:3.11-slim

# Install Chromium (lighter than Google Chrome, more stable in memory-constrained containers)
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    xvfb \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "bot_fully_automated.py"]
