import os

from docutils.parsers.rst.directives.images import Image

from sphinx.application import Sphinx

import auditinfo

class SharedImage(Image):
    """A wrapper for the `.. image::` directive to redirect into the repo's 'resources' dir

    This may be used just like the usual `.. image::` directive including all
    its options. The target path is assumed to be relative to 'resources' in
    the repository's root directory.
    """

    def run(self):
        img_path = os.path.join(auditinfo.global_resources(), self.arguments[0])
        doc_path = self.state.document.current_source
        self.arguments[0] = os.path.relpath(img_path, os.path.dirname(doc_path))
        return Image.run(self)

def setup(app: Sphinx):
    app.add_directive('sharedimg', SharedImage)

    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
