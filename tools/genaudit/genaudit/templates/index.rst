{{ document_title|rst_headline(1) }}

.. toctree::
   :hidden:

{% for topic in topics %}
   {{ topic }}
{% endfor %}
