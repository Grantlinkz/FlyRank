FROM python:3.11-slim

WORKDIR /app

# Install dependencies and Playwright Chromium with required OS libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install --with-deps chromium

# Copy application code
COPY . .

# Ensure artifact storage directory exists
RUN mkdir -p reports

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

