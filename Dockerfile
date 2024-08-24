## Use the official Python image as a base image
#FROM python:3.8-slim
#
## Set environment variables
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1
#
## Set the working directory in the container
#WORKDIR /app
#
## Copy the dependencies file to the working directory
#COPY requirements.txt .
#
## Install production dependencies and system libraries
##RUN apt-get update \
##    && apt-get install -y libsm6 libxext6 libgl1-mesa-glx \
##    && rm -rf /var/lib/apt/lists/*
##
##
##RUN apt-get update \
##    && apt-get install -y libglib2.0-0 libsm6 libtk8.6 libxrender1 libxext6
#
#RUN apt-get update \
#    && apt-get install -y libglib2.0-0 libsm6 libxext6 libxrender1 libgl1-mesa-glx libtk8.6 \
#    && rm -rf /var/lib/apt/lists/*
#
#
##RUN brew install glib
#RUN pip install --no-cache-dir -r requirements.txt
#
## Install Python dependencies including opencv-python
#RUN pip install --upgrade pip && \
#    pip install --no-cache-dir -r requirements.txt gunicorn opencv-python
#
#
## Copy the content of the local src directory to the working directory
#COPY . .
#
## Expose port 5000
#EXPOSE 8000
#
## Command to run the Flask application
#CMD exec gunicorn --bind :${PORT:-8000} --workers 1 --threads 8 --timeout 0 app:app


## Use the official Python image as a base image
#FROM python:3.8-slim
#
## Set environment variables
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1
#
## Set the working directory in the container
#WORKDIR /app
#
## Copy the dependencies file to the working directory
#COPY requirements.txt .
#
## Install production dependencies and system libraries
##RUN apt-get update \
##    && apt-get install -y libsm6 libxext6 libgl1-mesa-glx \
##    && rm -rf /var/lib/apt/lists/*
##
##
##RUN apt-get update \
##    && apt-get install -y libglib2.0-0 libsm6 libtk8.6 libxrender1 libxext6
#
#RUN apt-get update \
#    && apt-get install -y libglib2.0-0 libsm6 libxext6 libxrender1 libgl1-mesa-glx libtk8.6 \
#    && rm -rf /var/lib/apt/lists/*
#
#
##RUN brew install glib
#RUN pip install --no-cache-dir -r requirements.txt
#
## Install Python dependencies including opencv-python
#RUN pip install --upgrade pip && \
#    pip install --no-cache-dir -r requirements.txt gunicorn opencv-python
#
#
## Copy the content of the local src directory to the working directory
#COPY . .
#
## Expose port 5000
#EXPOSE 8000
#
## Command to run the Flask application
#CMD exec gunicorn --bind :${PORT:-8000} --workers 1 --threads 8 --timeout 0 app:app
## Use the official lightweight Python image.
## https://hub.docker.com/_/python
#FROM python:3.8
#
## RUN apt-get update \
## && apt-get install gcc -y \
## && apt-get clean
#
## Allow statements and log messages to immediately appear in the Knative logs
#ENV PYTHONUNBUFFERED True
#
#ENV OPENCV_VIDEOIO_PRIORITY_MATLAB 0
#
## Copy local code to the container image.
#ENV APP_HOME /app
#WORKDIR $APP_HOME
#COPY . ./
#
## Install production dependencies.
#RUN pip install --upgrade pip
#RUN apt-get update && apt-get install -y libsm6 libxext6
#RUN pip install -U opencv-python
#RUN pip install -r requirements.txt
#RUN pip install gunicorn
#
#
## Run the web service on container startup. Here we use the gunicorn
## webserver, with one worker process and 8 threads.
## For environments with multiple CPU cores, increase the number of workers
## to be equal to the cores available.
## Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
#CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app

# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.8

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies and system libraries
RUN apt-get update \
    && apt-get install -y libsm6 libxext6 libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies including opencv-python
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install gunicorn \
    && pip install opencv-python

# Run the web service on container startup using Gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
