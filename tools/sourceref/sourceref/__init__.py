from sourceref.role import SourceReferenceRole

from sphinx.application import Sphinx

def setup(app: Sphinx):
    app.add_config_value('src_ref_base_url', 'https://github.com/randombit/botan/blob', 'html')
    app.add_config_value('src_ref_reference', 'master', 'html')
    app.add_config_value('src_ref_check_url', False, 'env')

    app.add_role('srcref', SourceReferenceRole())

    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
