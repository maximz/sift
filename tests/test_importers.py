import sift.importers
from pytest import fixture

def test_markdown(datadir):
    # convert Path to str before sending to importer
    input_file = str(datadir.join('input.md'))
    with open(datadir.join('output.txt'), 'r') as expected_output:
        assert sift.importers.pandoc_importer.PandocImporter().run(input_file) == expected_output.read()

def test_pdf(datadir):
    # convert Path to str before sending to importer
    input_file = str(datadir.join('input2.pdf'))
    with open(datadir.join('output2.txt'), 'r') as expected_output:
        assert sift.importers.pdf_importer.PdfImporter().run(input_file) == expected_output.read()
