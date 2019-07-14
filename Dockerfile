FROM python:3.7

# Move files into Docker image
RUN mkdir /limiter
ADD requirements.txt /limiter/requirements.txt
ADD hello.py /limiter/hello.py
ADD rate_limiter_test.py /limiter/rate_limiter_test.py

# Install dependencies
RUN pip install -r /limiter/requirements.txt

# Run Flask on default port 5000 when the Docker container starts
ENTRYPOINT ["/bin/bash", "-c", "env FLASK_APP=/limiter/hello.py env FLASK_ENV=development flask run --host=0.0.0.0"]
