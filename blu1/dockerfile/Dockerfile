# Use the official Python image as a base image
FROM python:3.9

# Set the working directory to /app
WORKDIR /app

# Copy only the necessary files
COPY . /app
COPY wait-for-it.sh /app/wait-for-it.sh

# Make the script executable
RUN chmod +x /app/wait-for-it.sh



# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -v



# Run the Faust command
#CMD ["faust", "-A", "main", "worker"]
CMD ["sh", "-c", "./wait-for-it.sh kafka:9092 -- ./wait-for-it.sh connect:8083 -- python ./debezuim.py && echo 'Python script completed successfully' && faust -A main worker"]

