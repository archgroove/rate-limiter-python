# How decorators work

```
def logged(func):
    def with_logging(*args, **kwargs):
        print(func.__name__ + " was called")
        return func(*args, **kwargs)
    return with_logging


@logged
def f(x):
   """does some math"""
   return x + x * x


def f(x):
    """does some math"""
    return x + x * x
f = logged(f)
```

# Using wraps to prevent clobbering of docstring and __name__

```
from functools import wraps
def logged(func):
    @wraps(func)
    def with_logging(*args, **kwargs):
        print(func.__name__ + " was called")
        return func(*args, **kwargs)
    return with_logging

@logged
def f(x):
   """does some math"""
   return x + x * x

print(f.__name__)  # prints 'f'
print(f.__doc__)   # prints 'does some math'
```
