from sourceref.role import SourceReferenceRole

from sphinx.application import Sphinx

import auditinfo

def setup(app: Sphinx):
    app.add_config_value('src_ref_base_url', f'https://github.com/{auditinfo.botan_github_handle()}/blob', 'html')
    app.add_config_value('src_ref_reference', auditinfo.botan_git_ref(), 'html')
    app.add_config_value('src_ref_check_url', False, 'env')

    app.add_role('srcref', SourceReferenceRole())

    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
