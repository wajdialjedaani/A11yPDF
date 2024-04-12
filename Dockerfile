# Use the official Python image as a base image
FROM python:3.8-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install production dependencies and system libraries
#RUN apt-get update \
#    && apt-get install -y libsm6 libxext6 libgl1-mesa-glx \
#    && rm -rf /var/lib/apt/lists/*
#
#
#RUN apt-get update \
#    && apt-get install -y libglib2.0-0 libsm6 libtk8.6 libxrender1 libxext6

RUN apt-get update \
    && apt-get install -y libglib2.0-0 libsm6 libxext6 libxrender1 libgl1-mesa-glx libtk8.6 \
    && rm -rf /var/lib/apt/lists/*


#RUN brew install glib
RUN pip install --no-cache-dir -r requirements.txt

# Install Python dependencies including opencv-python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt gunicorn opencv-python


# Copy the content of the local src directory to the working directory
COPY . .

# Expose port 5000
EXPOSE 8000

# Command to run the Flask application
CMD exec gunicorn --bind :${PORT:-8000} --workers 1 --threads 8 --timeout 0 app:app
