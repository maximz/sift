from text_importer import TextImporter
from pandoc_importer import PandocImporter

IMPORTER_REGISTRY = {
    'txt': TextImporter,
    'md': PandocImporter,
    'pdf': PandocImporter,
    'doc': PandocImporter,
    'docx': PandocImporter,
}
