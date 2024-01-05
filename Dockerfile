# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV SECRET_KEY=my_secret_key
ENV MUSIC_CONFIG=your_database_url
ENV HOMMAR_CONFIG_DIR=hommar

# Run app.py when the container launches
CMD ["python", "main.py"]
