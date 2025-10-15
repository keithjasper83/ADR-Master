FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
COPY package.json .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Node dependencies and build CSS
RUN npm install
COPY tailwind.config.js .
COPY app/static/css/input.css ./app/static/css/
RUN npx tailwindcss -i ./app/static/css/input.css -o ./app/static/css/output.css --minify

# Copy application code
COPY app ./app

# Create directories
RUN mkdir -p plugins docs/adr

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
