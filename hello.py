#!/usr/bin/python
import logging
import sys
from flask import Flask
from limiter import Limiter

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
mylimiter = Limiter(app)


@app.route("/")
@mylimiter.limit(100, 'minute')
def hello():
    logging.info('Inside hello()')
    return "Hello, World!"


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, ssl_context='adhoc')  # TODO Remove debug in prod
