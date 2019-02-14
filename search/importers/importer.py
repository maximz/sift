class Importer(object):
    # semver
    version = 0.

    def read_file(self, full_path):
        """
        Returns contents of file at [full_path].
        Override if you expect binary data or want to preprocess with shell commands.
        """
        with open(full_path, 'r') as f:
            return f.read()

    def run(self, full_path):
        """
        Returns file contents ready for indexing. Not yet a packaged Lucene document.
        """
        pass
