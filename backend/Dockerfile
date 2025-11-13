# Use the official lightweight Python image.
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Set environment variables
ENV PORT=8080

# Expose port Cloud Run expects
EXPOSE 8080

# Run the Flask app using Gunicorn
CMD ["gunicorn", "-b", ":8080", "main:app"]
