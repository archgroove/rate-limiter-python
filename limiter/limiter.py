"""
Decorator that enforces rate limit on a Flask app. NB. Authorization must be
doen before the rate limiter is called.

Version: 0.1
"""
import sys
import typing
from functools import wraps
from flask import request
from flask import abort
from collections import namedtuple
from buffer import CircularBuffer

# In-memory databases used for rate limiting each endpoint.
# To scale this, keep only the highest priority users in the in-memory database,
# and the rest in a persistent database like Redis. A persistent store would
# also be better if you need to track the rate-limit across restarts.
databases = {}

class Limiter:
    """
    Keeps track of rate limits for a Flask app
    """

    def __init__(self, app):
        self.app = app
        pass

    @staticmethod
    def identity():
        """
        Get the unique id of the requester and the type of error code if this
        id is not available (eg. 401). The unique id could be an IP
        address, but since this can be spoofed and creates problems for users
        on shared networks, let's assume each authorized user has an api key.
        """
        Identity = namedtuple('Identity', ['unique_id', 'error_code'])
        # For demonstration purposes just pass the apikey in the url
        unique_id = request.args.get('apikey', default=None, type=str)
        # In production we should get apikey from authorization header like this:
        # unique_id = request.authorization["apikey"] or None
        error_code = 401
        identity = Identity(unique_id, error_code)
        return identity

    def _limit(self, rate: int, period: str, db_name: str, unique_id: str) -> int:
        """
        Helper class for the limit decorator which records this attempt to access
        the endpoint if it should succeed, and returns the number of seconds
        remaining until a user can access the endpoint again
        :db_name: str the name of the database for this limit (eg. endpoint
            function name or the name of a database shared between multiple
            endpoints)
        :unique_id: str unique identifier of the user accessing the endpoint
        """
        if not db_name in databases:
            databases[db_name] = {}
        database = databases[db_name]

        if not unique_id in database:
            database[unique_id] = CircularBuffer(rate, period)
        cbuffer = database[unique_id]

        if cbuffer.seconds_remaining == 0:
            cbuffer.put(datetime.datetime.now())

        return cbuffer.seconds_remaining()

    def limit(self, rate: int, period: str = 'hour', shared: str = None):
        """
        Decorator which allows a wrapped function to be called at most
        `rate` times per hour
        :rate: int the rate limit
        :period: str the time period over which the rate limit applies
        :shared: str the key to a shared in-memory database dictionary object
            for rate limits shared across multiple endpoints
        """
        def limit_decorator(func):
            @wraps(func)
            def limit_wrapper(*args, **kwargs):
                identity = self.identity()
                # A unique identity is required to keep track of rate limit
                if identity.unique_id == None:
                    abort(identity.error_code)
                seconds_remaining = self._limit(rate, period, shared or func.__name__, identity.unique_id)
                if seconds_remaining > 0:
                    abort(429, f"Rate limit exceeded. Try again in #{seconds_remaining} seconds")
                print(identity.unique_id + ' accessed ' + func.__name__, file=sys.stderr)
                return func(*args, **kwargs)
            return limit_wrapper
        return limit_decorator
