class Importer(object):
    # semver
    version = 0.

    def read_file(self, full_path):
        """
        Returns contents of file at [full_path].
        Override if you expect binary data or want to preprocess with shell commands.
        Ref: http://python-notes.curiousefficiency.org/en/latest/python3/text_file_processing.html#files-in-an-ascii-compatible-encoding-minimise-risk-of-data-corruption
        """
        with open(full_path, 'r', encoding="ascii", errors="surrogateescape") as f:
            return f.read()

    def run(self, full_path):
        """
        Returns file contents ready for indexing. Not yet a packaged Lucene document.
        """
        pass
