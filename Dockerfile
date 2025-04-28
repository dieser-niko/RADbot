# Use the official Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY ./src .

# Expose a port (modify if your app uses a specific port)
EXPOSE 8000

# Define the command to run your application (modify as needed)
CMD ["python", "app.py"]
