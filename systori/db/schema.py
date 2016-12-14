from tuath.backends.postgres import schema
from tsvector.schema import TriggerSchemaEditor


class DatabaseSchemaEditor(schema.DatabaseSchemaEditor):

    def forward_editor(self, method_name, *args, **kwargs):
        editor = TriggerSchemaEditor(self.connection)
        editor.deferred_sql = self.deferred_sql
        method = getattr(editor, method_name)
        method(*args, **kwargs)

    def create_model(self, model):
        super().create_model(model)
        self.forward_editor('create_model', model)

    def delete_model(self, model):
        super().delete_model(model)
        self.forward_editor('delete_model', model)

    def add_field(self, model, field):
        super().add_field(model, field)
        self.forward_editor('add_field', model, field)

    def remove_field(self, model, field):
        super().remove_field(model, field)
        self.forward_editor('remove_field', model, field)

    def alter_field(self, model, old_field, new_field, strict=False):
        super().alter_field(model, old_field, new_field)
        self.forward_editor('alter_field', model, old_field, new_field)
