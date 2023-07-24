{% macro short_author(author) %}`@{{ author.nick }} <{{ author.url }}>`_{% endmacro %}
{% macro short_authors_list(authors) %}{% for author in authors %}{{ short_author(author) }}{{ ", " if not loop.last else "" }}{% endfor %}{% endmacro %}
{% macro approvers_and_auditer_list(auditer, approvers) %}{% if approvers or auditer %}{{ short_authors_list(approvers) }}{% if approvers and auditer %}, {% endif %}{% if auditer %}({{ short_author(auditer) }}){% endif %}{% else %}none{% endif %}{% endmacro %}

{% macro full_author(author) %}{% if author.full_name %}{{ author.full_name }} ({% endif %}`@{{ author.nick }} <{{ author.url }}>`_{% if author.full_name %}){% endif %}{% endmacro %}

{% macro patch_reference(patch) %}{% if patch.type == "pull_request" %}`#{{ patch.github_ref }} <{{ patch.url }}>`_{%if patch.merge_commit %} (`{{ patch.merge_commit|truncate(7, true, "") }} <{{ patch.merge_commit_url }}>`_){% endif %}{% elif patch.type == "commit" %}`{{ patch.ref|truncate(7, true, "") }} <{{ patch.url }}>`_{% endif %}{% endmacro %}
