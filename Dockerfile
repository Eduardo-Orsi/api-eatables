# Use an appropriate base image, for example, Python 3.12
FROM python:3.12

# Set the working directory
WORKDIR /code

# Copy requirements file to the working directory
COPY ./requirements.txt /code/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the application code into the container
COPY ./app /code/app

# Expose port 8000 for FastAPI
EXPOSE 8000

# Command to run the FastAPI app with Uvicorn and SSL configuration
CMD ["uvicorn", "app.shipping:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-keyfile", "/path/to/privkey.pem", "--ssl-certfile", "/path/to/fullchain.pem"]
