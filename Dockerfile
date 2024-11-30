# Use the official Python image
FROM python:3.8-slim

# Install Rasa
RUN python -m pip install rasa

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Train the Rasa NLU model
RUN rasa train nlu

# Use a non-root user for security
USER 1001

# Default entrypoint and command for running Rasa
ENTRYPOINT ["rasa"]

CMD ["run", "--enable-api", "--port", "8080"]
