# Build on top of the latest Alpine version
FROM alpine:latest

# Install Python3 & pip3
RUN apk update && \
    apk upgrade && \
    apk add --no-cache python3 python3-dev py3-pip autoconf automake g++ make libffi-dev

# Get requirements, drop Dockerfile
COPY requirements.txt .

# Install python packages
RUN pip3 install -r requirements.txt

# Copy all other files
COPY . .

# Run script
CMD [ "python3", "app.py" ]
