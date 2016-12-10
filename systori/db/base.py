from django.db.backends.postgresql_psycopg2 import base
from .schema import DatabaseSchemaEditor


class DatabaseWrapper(base.DatabaseWrapper):
    SchemaEditorClass = DatabaseSchemaEditor
