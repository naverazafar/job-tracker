# Use official Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy project files into container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]