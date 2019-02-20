# Overview

# Install

Pull the docker image: `docker pull maximz/sift:latest`

Install a shell script to wrap the docker container:

```bash
echo 'function sift() { docker run --rm -t -v "$(pwd):/data" maximz/sift:latest sift ${@:1}; }' >> ~/.bashrc
source ~/.bashrc
```

# Use

```bash
sift -h
sift init
sift status
sift update
sift query [query]
```

## advanced

You can avoid the shell script and just run a docker container directly yourself:

```
# same as the shell script
docker run --rm -t -v "$(pwd):/data" maximz/sift:latest sift -h

# similar but mount files in read-only mode
mkdir -p .siftindex
docker run --rm -t -v "$(pwd):/data:ro" -v "$(pwd)/.siftindex:/data/.siftindex" maximz/sift:latest sift -h
```

See also command line flags to change index location.

# Develop

```
docker build -t maximz/sift . # build and run tests
```

## Todos

* `.searchignore`
* error handling for file import. don't pass-through the failed imports to new index state
* shorter fragments for highlighting