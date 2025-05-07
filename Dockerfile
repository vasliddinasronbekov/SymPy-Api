# Use a specific Python version as the base image
FROM python:3.10-slim
# Set the working directory inside the container
WORKDIR /app
# Copy the requirements file into the container at /app
COPY requirements.txt .
# Upgrade pip (optional but recommended)
RUN pip install --upgrade pip
# Install the dependencies defined in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Copy the rest of the application code into the container
COPY . .
# Expose the necessary port
EXPOSE 5000
# Command to run the application
CMD ["python", "app.py"]  # Change app.py to your main application file
