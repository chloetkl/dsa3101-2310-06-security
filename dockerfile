# Use an official Python runtime as a parent image
FROM python:3.10.6-slim-buster

# Set the working directory within the container
WORKDIR /app


COPY nusecure.py nusecure.py
COPY static static
COPY templates templates
COPY requirements.txt requirements.txt
COPY requirements.txt requirements.txt


# Install any needed packages specified in requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
# CMD ["python", "nusecure.py"]

ENTRYPOINT python -u -m nusecure
