from .importer import Importer
import pypandoc

"""
Runs pandoc on input file to convert to plain text.
However, "plain" means Gutenberg style for pandoc:
>    + Emphasis is rendered with `_underscores_`, strong emphasis
>      with ALL CAPS.
>    + Headings are rendered differently, with space to set them off,
>      not with setext style underlines. Level 1 headers are ALL CAPS.

Ref:
* https://github.com/jgm/pandoc/blob/6d91fb25639c6ac985d15c7112e009533d06e5f2/changelog#L1903
* https://github.com/jgm/pandoc/issues/3766
* https://groups.google.com/forum/#!msg/pandoc-discuss/spfSz1CDm6U/zmU_uUZ2IKUJ
* https://github.com/jgm/pandoc/blob/master/test/Tests/Writers/Plain.hs
* https://stackoverflow.com/a/34139581/130164

In future consider https://github.com/remarkjs/strip-markdown
"""

class PandocImporter(Importer):
    version = 1.
    def run(self, full_path):
        return pypandoc.convert_file(
            full_path,
            'plain',
            extra_args=['--base-header-level=2'] # avoids level 1 headers becoming ALL CAPS
        )
