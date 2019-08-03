FROM python:3.7

# Move files into Docker image
ADD requirements.txt /requirements.txt
ADD hello.py /hello.py
ADD limiter /limiter

# Install dependencies
WORKDIR /
RUN pip install -r requirements.txt

WORKDIR /limiter
RUN python setup.py install

# Run Flask on default port 5000 when the Docker container starts
WORKDIR /
ENTRYPOINT ["/bin/bash", "-c", "env FLASK_APP=hello.py env FLASK_ENV=development flask run --host=0.0.0.0"]
