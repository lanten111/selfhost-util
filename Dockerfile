# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt.old
RUN pip install -r requirements.txt

RUN mkdir /homarr_config_folder

RUN mkdir /music_config_folder

RUN mkdir /flame_db_folder

# Define environment variable
ENV SECRET_KEY=my_secret_key

# Run app.py when the container launches
CMD ["python", "main.py"]
