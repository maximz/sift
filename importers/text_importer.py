from importer import Importer, Document
class TextImporter(Importer):
    version = 1.
    def execute(self, full_path):
        d = Document()
        d.text = self.read_file(full_path)
        return d