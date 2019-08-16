"""
Decorator that enforces rate limit on a Flask app. The current implementation uses an
in-memory database with a circular buffer for each user that gets populated
with a maximum number of entries which depends on the rate limit.

NB. Authorization must be
done before the rate limiter is called.

Version: 0.1

TODO:
[ ] research more performant concurrency support
[ ] use authorization headers to get user id
[ ] add periodic persistent storage to handle unexpected downtime
[ ] add persistent storage to handle users that can't fit in memory
[ ] Add binary search of the circular buffer to quickly find the last out-of-date entry
"""
import logging
import sys
import typing
from threading import Lock
from datetime import datetime, timedelta
from functools import wraps
from flask import request
from flask import abort
from collections import namedtuple
from circular_buffer import CircularBuffer

# Variable points to the in-memory databases used for rate limiting each endpoint.
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

    def _clear_buffer(self, cbuffer: dict, period: timedelta, now: datetime):
        # TODO use a binary search to find the oldest expired entry
        # TODO make this a method of a circular_buffer subclass that only
        # accepts timestamps
        index = 0
        while index < cbuffer.size and cbuffer[index] < now - period:
            index += 1
        cbuffer.remove_from_start(index)

    def _record_access(self, cbuffer: dict, now: datetime) -> bool:
        """
        Creates the rate limit database for this endpoint or shared rate limit if
        it does not exist, and records the access if it should succeed. Returns
        True if the access should succeed.
        """
        if not cbuffer.is_full():
            cbuffer.add_to_end(now)
            return True
        return False

    def _seconds_remaining(self, now: datetime, period: timedelta, cbuffer: dict) -> int:
        """Get the number of seconds remaining before a user can access an endpoint"""
        # A database for this endpoint and a buffer for this user must exist
        if not cbuffer.is_full():
            return 0
        limit_expires = cbuffer[0] + period
        time_remaining_seconds = max(0, (limit_expires - now).total_seconds())
        return int(time_remaining_seconds)

    def _get_period_from_string(self, period_str: str) -> timedelta:
        """Convert a rate limiting period string to a timedelta object"""
        # TODO implement logic to handle other rate limiting periods
        if period_str == 'hour':
            period = timedelta(hours=1)
        elif period_str == 'minute':
            period = timedelta(minutes=1)
        else:
            raise ValueError(f"{period_str} is not a supported time period")
        return period

    def _limit(self, rate: int, period: timedelta, limit_name: str, unique_id: str) -> bool:
        """
        Tries to record an access to the endpoint in a database. The database
        limites the number of entries up to the rate limit, and consequently a
        failure to add the access to the database indicates that access to the
        endpoint should fail. Returns True on success.

        rate -- the rate limit
        period -- the time period over which the rate limit applies (timedelta)
        endpoint_name -- the name of the endpoint or shared rate limit to which
            the rate limit applies
        unique_id -- a unique identifier for the user accessing the endpoint
        """
        # Create a database for this endpoint if it doesn't exist
        if not limit_name in databases:
            databases[limit_name] = {}
        database = databases[limit_name]

        # Create an buffer and lock for this user if it doesn't exist
        if not unique_id in database:
            database[unique_id] = {'buffer': CircularBuffer(rate), 'lock': Lock()}
        cbuffer = database[unique_id]['buffer']
        lock = database[unique_id]['lock']

        now = datetime.now()

        with lock:
            self._clear_buffer(cbuffer, period, now)
            succeeded = self._record_access(cbuffer, now)
            logging.info(limit_name + ' accessed by ' + unique_id +
                         ' ' + str(cbuffer.size) + ' times in the last ' + str(period) + 'h')
            if not succeeded:
                s = self._seconds_remaining(now, period, cbuffer)
                abort(429, f"Rate limit exceeded. Try again in #{s} seconds")


    def limit(self, rate: int, period_str: str, shared: str = None):
        """
        Decorator which allows a wrapped function to be called at most
        `rate` times per time period defined in `period_str`

        rate -- the rate limit
        period_str -- the time period over which the rate limit applies
        shared -- the key to a shared in-memory database dictionary object
            for rate limits shared across multiple endpoints. If this is not
            supplied, the limit is applied only to the endpoint this function wraps
        """
        period = self._get_period_from_string(period_str)

        def limit_decorator(func):
            @wraps(func)
            def limit_wrapper(*args, **kwargs):
                # A unique identity is required to keep track of rate limit
                identity = self.identity()
                if identity.unique_id == None:
                    abort(identity.error_code)
                self._limit(rate, period, shared or func.__name__, identity.unique_id)
                return func(*args, **kwargs)
            return limit_wrapper
        return limit_decorator
