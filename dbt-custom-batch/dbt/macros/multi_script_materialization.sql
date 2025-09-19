{% materialization multi_script, adapter='bigquery' -%}
  {# Setup #}
  {{ run_hooks(pre_hooks) }}

  {# there can be several ref() or source() according to BQ copy API docs #}
  {# cycle over ref() and source() to create source tables array #}
  {% set source_array = [] %}
  {% for ref_table in model.refs %}
    {{ source_array.append(ref(ref_table.get('package'), ref_table.name, version=ref_table.get('version'))) }}
  {% endfor %}

  {% for src_table in model.sources %}
    {{ source_array.append(source(*src_table)) }}
  {% endfor %}

  {# retrieving sets to iterate over #}

  {% for row in run_query(config.get('iterate_over')) %}
    {{ log("Processing row: " ~ row, info=True) }}
  {% endfor %}


  {{ store_result('main', response=config.get('iterate_over')) }}

  {# Clean up #}
  {{ run_hooks(post_hooks) }}
  {%- do apply_grants(target_relation, grant_config) -%}
  {{ adapter.commit() }}

  {{ return({'relations': []}) }}
{%- endmaterialization %}
