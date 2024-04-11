# Use the official Python image as a base image
FROM python:3.8

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

RUN pip install -r requirements.txt

# Install production dependencies and system libraries
RUN apt-get update \
    && apt-get install -y libsm6 libxext6 libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies including opencv-python
RUN pip install --upgrade pip \
    && pip install gunicorn \
    && pip install opencv-python

# Copy the content of the local src directory to the working directory
COPY . .

# Expose port 5000
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "app.py"]
