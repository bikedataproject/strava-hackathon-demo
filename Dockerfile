# Build on top of the latest Alpine version
FROM alpine:latest

# Install Python3 & pip3
RUN apk update && \
    apk upgrade && \
    apk add --no-cache python3 python3-dev py3-pip autoconf automake g++ make libffi-dev

# Get files, drop Dockerfile
COPY . .

# Install python packages
RUN pip3 install -r requirements.txt

# Run script
CMD [ "python3", "app.py" ]