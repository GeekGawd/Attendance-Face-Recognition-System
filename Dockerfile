# Use an official Python runtime as a parent image
FROM python:3.6

RUN adduser -u 5678 --disabled-password --gecos "" appuser && \
    adduser appuser video && \
    chown -R appuser /app
USER appuser

# Install git
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

WORKDIR /app/bcolz-windows

RUN python setup.py install

WORKDIR /app

RUN pip install --no-deps torchvision==0.4.1

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "main.py"]
