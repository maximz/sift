# overview

# install

```bash
docker run --rm -t -v "$(pwd):/data" maximz/sift:latest search -h

mkdir -p .siftindex
docker run --rm -t -v "$(pwd):/data:ro" -v "$(pwd)/.siftindex:/data/.siftindex" maximz/sift:latest search status | less
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

# todos

* error handling for file import. don't pass-through the failed imports to new index state
* shorter fragments for highlighting