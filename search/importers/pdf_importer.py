from .importer import Importer, Document
import subprocess

class PdfImporter(Importer):
    version = 1.
    def run(self, full_path):
        d = Document()
        d.text = subprocess.run(
            ['pdftotext', '-q', full_path, '-'], stdout=subprocess.PIPE, check=True, universal_newlines=True).stdout
        return d
