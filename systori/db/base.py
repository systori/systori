from django.db.backends.postgresql import base
from postgres_schema import schema as postgres_schema
from tsvector_field import schema as tsvector_schema


class DatabaseWrapper(base.DatabaseWrapper):
    SchemaEditorClass = type(
        "DatabaseSchemaEditor",
        (postgres_schema.DatabaseSchemaEditor, tsvector_schema.DatabaseSchemaEditor),
        {},
    )
