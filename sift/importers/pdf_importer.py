from .importer import Importer
import subprocess

class PdfImporter(Importer):
    version = 1.
    def run(self, full_path):
        return subprocess.run(
            ['pdftotext', '-q', full_path, '-'], stdout=subprocess.PIPE, check=True, universal_newlines=True).stdout
