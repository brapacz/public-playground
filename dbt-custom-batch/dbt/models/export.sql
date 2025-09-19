{% set iterate_over %}
SELECT DISTINCT event, date
FROM {{ ref('dogs') }}
{% endset %}

{{config(
    materialized='multi_script',
    iterate_over=iterate_over,
    parallel=True
)}}

EXPORT DATA OPTIONS(
  uri='gs://dev_brapacz_tivo_mpcs/batch_exports_tests/dogs/events/{{ event }}/date={{ date }}/*.csv',
  format='CSV',
  overwrite=true,
  header=true,
  field_delimiter=','
) AS (
    SELECT * FROM {{ ref('dogs') }}
    WHERE event = '{{ event }}' AND date = '{{ date }}'
);
