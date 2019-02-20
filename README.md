# `sift`: a git-inspired personal search utility

**Use cases:**

* I have a large collection of markdown notes and grep is just not cutting it anymore for search.
    * `sift` gives you simple conversion of markdown to text and then indexing for fuzzy search.

* Avoid painful and expensive online storage system searches by indexing files before moving them to long-term storage.
    * With `sift`, it's easy to index a set of files before moving them to a cold-line backup service like Amazon S3's Glacier service. which has substantial data retrieval costs.
    * Search your local index to find the file paths you care about, avoiding time substantial data retrieval costs and time it would take to walk through s3 on your own.

* Make your hard-to-search files much easier to search.
    * `sift` ships with importers for Word documents, PDFs, Markdown files, and text files. It's easy to add your own to convert any file type to text and then index all such files on your hard drive.

**How it works:**

* Custom importers to convert different file types to text for indexing. Easily extensible to new file types. Calls out to `pandoc`, `pdftotext`, etc.
* Under the hood, search is powered by Lucene -- the backbone of Solr and Elasticsearch.
* A lightweight metadata manager to track last-indexed times.

# Install

Pull the docker image: `docker pull maximz/sift:latest`

Install a shell script to wrap the docker container:

```bash
echo 'function sift() { docker run --rm -t -v "$(pwd):/data" maximz/sift:latest sift ${@:1}; }' >> ~/.bashrc
source ~/.bashrc
```

# Use

```bash
> sift -h
usage: sift [-h] [--path PATH] {init,status,update,query,q} ...

Index a file tree and search it.

positional arguments:
  {init,status,update,query,q}
    init                Init index
    status              Status of index
    update              Update index
    query (q)           Query index

optional arguments:
  -h, --help            show this help message and exit
  --path PATH           Index path
```

Quick walkthrough:

```bash
# init index
sift init
# see what's changed since last index
sift status
# apply changes to index
sift update
# search the index
sift query [query terms]
```

## Advanced

You can avoid the shell script and just run a docker container directly yourself:

```bash
# same as the shell script
docker run --rm -t -v "$(pwd):/data" maximz/sift:latest sift -h

# similar but mount files in read-only mode
mkdir -p .siftindex
docker run --rm -t -v "$(pwd):/data:ro" -v "$(pwd)/.siftindex:/data/.siftindex" maximz/sift:latest sift -h
```

See also command line flags to change index location.

# Develop

Build and run tests: `docker build -t maximz/sift .`

## Todos

* Extend search cli to support date range queries.
* Build `.siftignore` to disable indexing for certain file types.
* Error handling for file import. don't pass-through the failed imports to new index state
* Shorter fragments for highlighting
* Add importers for more file types.