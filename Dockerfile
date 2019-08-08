FROM python:3.7

# Add the user UID:1000, GID:1000, home at /app
RUN groupadd -r app -g 1000 && useradd -u 1000 -r -g app -m -d /app -s /sbin/nologin -c "App user" app && \
    chmod 755 /app

# Move files into Docker image
ADD requirements.txt /app/requirements.txt
ADD hello.py /app/hello.py
ADD limiter /app/limiter

# Install dependencies
WORKDIR /app
RUN pip install -r requirements.txt

WORKDIR /app/limiter
RUN python setup.py install

# Switch to app user and run Flask on default port 5000
WORKDIR /app
USER app
ENTRYPOINT ["/bin/bash", "-c", "env FLASK_APP=hello.py env FLASK_ENV=development flask run --host=0.0.0.0 --cert=adhoc"]
