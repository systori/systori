from drf_yasg.openapi import SchemaRef


def recursive_merge(schema, override_schema):
    """
    Currently the swagger_schema_fields overrides the generated Schema object.
    This does a deep merge instead.

    See https://github.com/axnsan12/drf-yasg/issues/291
    """
    for attr, val in override_schema.items():
        schema_val = schema.get(attr, None)
        if isinstance(schema_val, SchemaRef):
            # Can't merge SchemaRef with dict, replace the whole object
            schema[attr] = val
        elif isinstance(val, dict):
            if schema_val:
                recursive_merge(schema_val, val)
            else:
                schema[attr] = val
        else:
            schema[attr] = val


def add_manual_fields(self, serializer_or_field, schema):
    """
    Changes the behavior to do a deep merge when swagger_schema_fields is defined
    """
    meta = getattr(serializer_or_field, "Meta", None)
    swagger_schema_fields = getattr(meta, "swagger_schema_fields", {})
    if swagger_schema_fields:
        recursive_merge(schema, swagger_schema_fields)
