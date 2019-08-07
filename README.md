# Python version

Python 3.7

# Run the example app

From outside the project folder, run the following commands, substituting
<name:tag> for some some new docker image name and optionally a tag.
If you don't want to accidentally overwrite an existing name:tag combination,
first check your existing list using `docker image ls`

```
docker build -t <name:tag> rate-limiter-python/
docker run -it -p 5000:5000 <name:tag>
```

You should see the following:
 * Serving Flask app "hello"
 * Running on https://0.0.0.0:5000/ (Press CTRL+C to quit)

Navigate to https://localhost:5000?apikey=user.

Since we're using a dummy certificate to authenticate this for demonstration
purposes, you will see a security warning. Since localhost is secure, it is
fine to accept this warning and proceed to the page.

NB. If port 5000 is already occupied, change the second occurrence of 5000
in the docker run command to an unoccupied port, and change the port of the
app address to the same thing.

# Run the tests


# Programming guidelines

The name of the function which the limit decorator wraps is used as the key
of the database (implemented as a dictionary) which records the number and time
of accesses to the endpoint. If you change a function name, you will need to
update the corresponding key.

If you want to implement a rate limit that is shared across multiple endpoints,
you must provide a unique name for this shared rate limit which will be used
as the key of the database (dictionary). This must not be the same of the name
of any endpoint function.
