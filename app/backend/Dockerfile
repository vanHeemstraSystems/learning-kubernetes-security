FROM python:3.11-slim

# Create non-root user

RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory

WORKDIR /app

# Copy requirements first for better caching

COPY requirements.txt .

# Install dependencies

RUN pip install –no-cache-dir -r requirements.txt

# Copy application code

COPY app.py .

# Change ownership to non-root user

RUN chown -R appuser:appuser /app

# Switch to non-root user

USER appuser

# Expose port

EXPOSE 5000

# Health check

HEALTHCHECK –interval=30s –timeout=3s –start-period=5s –retries=3   
CMD python -c “import urllib.request; urllib.request.urlopen(‘http://localhost:5000/health’)” || exit 1

# Run with gunicorn for production

CMD [“gunicorn”, “–bind”, “0.0.0.0:5000”, “–workers”, “2”, “–timeout”, “60”, “app:app”]
