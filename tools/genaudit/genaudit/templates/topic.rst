{% import 'macros.rst' as macros %}
.. _changes/{{ reference }}:

{{ title|rst_headline(1) }}

Security Classification: *{{ classification }}*

{% if authors %}
{{ "Code authors"|rst_headline(2) }}

{% for author in authors %}
* {{ macros.full_author(author) }}
{% endfor %}
{% endif %}

{% if description %}
{{ "Description"|rst_headline(2) }}

{{ description|trim }}
{% endif %}

{% if patches %}
{{ "Relevant Patches"|rst_headline(2) }}

.. list-table::
   :class: longtable
   :widths: 10 50 10 15 15
   :header-rows: 1

   * - Ref.
     - Patch title / Audit comment
     - Impact
     - Author
     - Approver(s)
{% for patch in patches %}
{% if patch.type == "pull_request" %}
   * - {{ macros.patch_reference(patch) }}
     - {% if patch.comment %}**{{ patch.title|escape_rst }}**

       {{ patch.comment|trim|indent(7) }}
       {% else %}{{ patch.title|escape_rst }}
       {% endif %}
     - {{ patch.classification }}
     - {{ macros.short_author(patch.author) }}
     - {{ macros.approvers_and_auditer_list(patch.auditer, patch.approvers) }}
{% elif patch.type == "commit" %}
   * - {{ macros.patch_reference(patch) }}
     - {% if patch.comment %}**{{ patch.message|first_line|escape_rst }}**

       {{ patch.comment|trim|indent(7) }}
       {% else %}{{ patch.message|first_line|escape_rst }}
       {% endif %}
     - {{ patch.classification }}
     - {{ macros.short_author(patch.author) }}
     - {% if patch.auditer %}({{ macros.short_author(patch.auditer) }}){% else %}none{% endif +%}
{% endif %}
{% endfor %}
{% endif %}

.. raw:: latex

   \pagebreak
