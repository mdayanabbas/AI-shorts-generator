# Start with an official Python base image
FROM python:3.9-slim

# Install FFmpeg - the video processing engine
RUN apt-get update && apt-get install -y ffmpeg

# Set the working directory inside the container
WORKDIR /app

# Copy the file that lists our Python dependencies
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Tell Docker that our app will listen on port 5000
EXPOSE 5000

# The command to run when the container starts
CMD ["python", "app.py"]