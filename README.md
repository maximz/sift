# `sift`: a git-inspired personal search utility

[![CircleCI](https://circleci.com/gh/maximz/sift/tree/master.svg?style=shield)](https://circleci.com/gh/maximz/sift/tree/master)

**Use cases:**

* I have a large collection of markdown notes and grep is just not cutting it anymore for search.
    * `sift` gives you simple conversion of markdown to text and then indexing for fuzzy search.

* Avoid painful and expensive online storage system searches by indexing files before moving them to long-term storage.
    * With `sift`, it's easy to index a set of files before moving them to a cold-line backup service like Amazon S3's Glacier service. which has substantial data retrieval costs.
    * Search your local index to find the file paths you care about, avoiding time substantial data retrieval costs and time it would take to walk through s3 on your own.

* Make your hard-to-search files -- whether they are Word, LaTeX, or PDF documents -- much easier to search.
    * `sift` ships with importers for many file types. With `sift`, your collection of LaTex notes now has rich full-text search. It's easy to add your own to convert any file type to text and then index all such files on your hard drive.

_Full list of currently supported file types:_

* `.txt`
* `.md`
* `.pdf`
* `.doc`
* `.docx`
* `.tex`
* `.latex`
* `.html`
* `.epub`
* [add your own...](https://github.com/maximz/sift/blob/master/sift/importers/registry.py)

**How it works:**

* Custom importers to convert different file types to text for indexing. Easily extensible to new file types. Calls out to `pandoc`, `pdftotext`, etc.
* Under the hood, search is powered by Lucene -- the backbone of Solr and Elasticsearch.
* A lightweight metadata manager to track last-indexed times.

# Install

1. Install Docker.

2. Pull the docker image: `docker pull maximz/sift:latest`

3. Install a shell script to wrap the docker container:

```bash
echo 'function sift() { docker run --rm -t -v "$(pwd):/data" maximz/sift:latest sift ${@:1}; }' >> ~/.bashrc
source ~/.bashrc
```

4. Test your installation:

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

# Tutorial

Install `sift` by following the above instructions. Then run through this walkthrough:

## Getting started

```bash
# clone the repo
> git clone https://github.com/maximz/sift.git

# open example directory
> cd sift/example

# this directory contains a number of example files that we'll index
> find .
.
./pandoc_manual.tex
./books
./books/wonderland.html
./books/frankenstein.epub

# create index
> sift init
Index created
```

## Indexing files

```bash
# identify files that need to be indexed
> sift status
New:
pandoc_manual.tex
books/wonderland.html
books/frankenstein.epub

# apply changes to index
> sift update
Inserted: pandoc_manual.tex
Inserted: books/wonderland.html
Inserted: books/frankenstein.epub

# now there are no more files to be indexed
> sift status
# quiet output

# make some changes
> cp pandoc_manual.tex pandoc_manual.latex
> touch books/wonderland.html

# see what's changed since last index
> sift status
New:
pandoc_manual.latex
Updated:
books/wonderland.html

# update the index
> sift update
Inserted: pandoc_manual.latex
Updated: books/wonderland.html

# now there are no more files to be indexed
> sift status

# delete a file
> rm pandoc_manual.latex

# re-run status
> sift status
Deleted:
pandoc_manual.latex

# by default, update will not remove deleted files from index.
> sift update
Missing objects NOT removed from index.

# read docs for this behavior
> sift update -h
usage: sift update [-h] [--delete-missing]

optional arguments:
  -h, --help        show this help message and exit
  --delete-missing  Delete files that no longer exist

# force removal of delete file from index.
> sift update --delete-missing
Deleted: pandoc_manual.latex
Missing objects removed from index.

# status is quiet, no more files to be indexed
> sift status
```

## Let's get searching

```bash
# search the index
> sift query alice
Results for: alice
=== books/wonderland.html (2019-03-01 03:55:09 UTC) ===


*Alice* was beginning to get very tired of sitting by her sister on the
bank, and of having nothing... or conversations in
it, ‘and what is the use of a book,’ thought *Alice* ‘without pictures or
conversations....

There was nothing so _very_ remarkable in that; nor did *Alice* think it
so _very_ much out of the way

# run another query
> sift query gutenberg
Results for: gutenberg
=== books/wonderland.html (2019-03-01 03:55:09 UTC) ===
 it, give it away or
    re-use it under the terms of the Project *Gutenberg* License included...

    Language: English

    Character set encoding: UTF-8

    *** START OF THIS PROJECT *GUTENBERG* EBOOK

=== books/frankenstein.epub (2019-03-01 03:16:41 UTC) ===
 it away or
re-use it under the terms of the Project *Gutenberg* License included
with this eBook...: English
*** START OF THIS PROJECT *GUTENBERG* EBOOK FRANKENSTEIN ***
Produced by Judith Boss

# one more query
> sift query library wonder
Results for: library wonder
=== books/wonderland.html (2019-03-01 03:55:09 UTC) ===
, or she fell very slowly, for she had
plenty of time as she went down to look about her and to *wonder*... *wonder* how
many miles I’ve fallen by this time?’ she said aloud. ‘I must be getting
somewhere near... it was good practice to say it
over) ‘—yes, that’s about the right distance—but then I *wonder* what

=== books/frankenstein.epub (2019-03-01 03:16:41 UTC) ===
’ *library*. My education was neglected, yet I was
passionately fond of reading. These volumes were my....

This appearance excited our unqualified *wonder*. We were, as we believed,
many hundred miles from any land....

The peasant woman, perceiving that my mother fixed eyes of *wonder* and
admiration on this lovely

=== pandoc_manual.tex (2019-03-01 03:16:37 UTC) ===
pandoc [_options_] [_input-file_]…

Pandoc is a Haskell *library* for converting from one markup format to
another, and a command-line tool that uses this *library*.

Pandoc can convert between numerous... output. The _URL_ is
    the base URL for the KaTeX *library*. That directory should contain

```

# Develop

Close the repo, then run `docker build -t sift .` to build and run tests.

## Advanced use

You can avoid the shell script and just run a docker container directly yourself:

```bash
# same as the shell script
docker run --rm -t -v "$(pwd):/data" maximz/sift:latest sift -h

# similar but mount files in read-only mode
mkdir -p .siftindex
docker run --rm -t -v "$(pwd):/data:ro" -v "$(pwd)/.siftindex:/data/.siftindex" maximz/sift:latest sift -h
```

## Todos

* Extend search cli to support date range queries.
* Build `.siftignore` to disable indexing for certain file types.
* Error handling for file import. don't pass-through the failed imports to new index state
* Shorter fragments for highlighting
* Add importers for more file types.