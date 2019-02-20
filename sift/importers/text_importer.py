from .importer import Importer
class TextImporter(Importer):
    version = 1.
    def run(self, full_path):
        return self.read_file(full_path)