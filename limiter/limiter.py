"""
Decorator that enforces rate limit on a Flask app

Version: 0.1
"""
import sys
from functools import wraps



class Limiter:
    """
    Keeps track of rate limits for a Flask app
    """

    def __init__(self, app):
        self.app = app
        pass

    def limit(self, rate):
        """
        Decorator which allows a wrapped function to be called at most
        `rate` times per day
        """
        def limit_decorator(func):
            @wraps(func)
            def limit_wrapper(*args, **kwargs):
                print('Limit was called', file=sys.stderr)
                return func(*args, **kwargs)
            return limit_wrapper
        return limit_decorator
