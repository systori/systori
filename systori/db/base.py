from django.db.backends.postgresql import base
from .schema import DatabaseSchemaEditor


class DatabaseWrapper(base.DatabaseWrapper):
    SchemaEditorClass = DatabaseSchemaEditor
