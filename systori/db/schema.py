from tuath.backends.postgres import schema
from .fields import TSVectorField
from collections import OrderedDict


class DatabaseSchemaEditor(schema.DatabaseSchemaEditor):

    sql_create_trigger_function = (
        "CREATE FUNCTION {function}() RETURNS trigger AS $$\n"
        "BEGIN\n"
        " NEW.{column} :=\n{weights};\n"
        " RETURN NEW;\n"
        "END\n"
        "$$ LANGUAGE plpgsql;"
    )

    sql_create_trigger = (
        "CREATE TRIGGER {trigger} BEFORE INSERT OR UPDATE"
        " ON {table} FOR EACH ROW EXECUTE PROCEDURE {function}();"
    )

    sql_setweight = (
        "  setweight("
            "to_tsvector('pg_catalog.{lang}', COALESCE(NEW.{column}, '')), "
            "'{weight}') "
    )

    def _create_tsvector_trigger(self, model, field):

        tsvector_function = self._create_index_name(model, [field.column], '_func')
        tsvector_trigger = self._create_index_name(model, [field.column], '_trig')

        weights = []
        for tsv in field.columns:
            weights.append(
                self.sql_setweight.format(
                    lang=field.language,
                    column=self.quote_name(tsv.name),
                    weight=tsv.weight
                )
            )

        yield self.sql_create_trigger_function.format(
            function=tsvector_function,
            column=self.quote_name(field.column),
            weights='||\n'.join(weights)
        )

        yield self.sql_create_trigger.format(
            table=self.quote_name(model._meta.db_table),
            trigger=self.quote_name(tsvector_trigger),
            function=tsvector_function,
        )

    def _model_indexes_sql(self, model):
        output = super()._model_indexes_sql(model)

        if not model._meta.managed or model._meta.proxy or model._meta.swapped:
            return output

        for field in model._meta.local_fields:
            if isinstance(field, TSVectorField):
                output.extend(self._create_tsvector_trigger(model, field))

        return output
