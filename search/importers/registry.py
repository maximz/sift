from .text_importer import TextImporter
from .pandoc_importer import PandocImporter
from .pdf_importer import PdfImporter

"""
Whitelist of acceptable file extensions is maintained here.
Each extension is mapped to the importer strategy to be executed.
"""

IMPORTER_REGISTRY = {
    'txt': TextImporter,
    'md': PandocImporter,
    'pdf': PdfImporter,
    'doc': PandocImporter,
    'docx': PandocImporter,
}
