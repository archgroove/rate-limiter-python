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
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

# Run the tests
