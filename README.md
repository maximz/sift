# overview

# install

```bash
docker run --rm -it -v "$(pwd):/data" maximz/sift:latest search -h
```

# use

```bash
search status
search update
search -- [query]
```

# advanced

`.searchignore`

```
docker build -t maximz/sift . # build and run tests
```