# Use official Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose both ports
EXPOSE 8000
EXPOSE 8501

# Run both services
CMD ["/start.sh"]

