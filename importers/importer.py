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

    def execute(self, full_path):
        """
        Returns a Document ready for indexing.
        """
        pass


class Document(object):
    pass
