# Use an official Python runtime as a parent image
FROM python:3.10.6-slim-buster

# Set the working directory to /app
WORKDIR /app

<<<<<<< HEAD
COPY . .
=======
COPY nusecure.py nusecure.py
COPY static static
COPY templates templates
COPY requirements.txt requirements.txt
>>>>>>> d00846954874a39f01f5d4be11d882adc0967496

# Install any needed packages specified in requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP nusecure

ENTRYPOINT python -u -m nusecure

# Run app.py when the container launches
<<<<<<< HEAD
# CMD ["python", "nusecure.py"]
=======
CMD ["python", "app.py"]
>>>>>>> d00846954874a39f01f5d4be11d882adc0967496
