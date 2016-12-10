from django.test import TestCase
from django.db import models, connection
from django.db.migrations.writer import MigrationWriter
from .fields import TSVectorField, TSVector


class TextDocument(models.Model):
    class Meta:
        app_label = 'test'
    name = models.CharField(max_length=128)
    description = models.TextField()
    tsv = TSVectorField([
        TSVector('name', 'A'),
        TSVector('description', 'D'),
    ], 'german')


class SearchVectorFieldTestCase(TestCase):

    def test_deconstruct(self):
        tsv = TSVectorField([
            TSVector('name', 'A'),
            TSVector('description', 'D'),
        ], 'german')
        self.assertEqual(
            ("systori.db.fields.TSVectorField("
                "columns=["
                    "systori.db.fields.TSVector('name', 'A'), "
                    "systori.db.fields.TSVector('description', 'D')], "
                "language='german')",
             {'import systori.db.fields'}),
            MigrationWriter.serialize(tsv)
        )

    def test_sql(self):
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(TextDocument)
            self.assertEqual([
                'CREATE INDEX "test_textdocument_tsv_59565b71" ON "test_textdocument" ("tsv")',
                'CREATE FUNCTION test_textdocument_tsv_59565b71_func() RETURNS trigger AS $$\n'
                'BEGIN\n'
                ' NEW."tsv" :=\n'
                '  setweight(to_tsvector(\'pg_catalog.german\', COALESCE(NEW."name", \'\')), \'A\') ||\n'
                '  setweight(to_tsvector(\'pg_catalog.german\', COALESCE(NEW."description", \'\')), \'D\') ;\n'
                ' RETURN NEW;\n'
                'END\n'
                '$$ LANGUAGE plpgsql;',
                'CREATE TRIGGER "test_textdocument_tsv_59565b71_trig" BEFORE INSERT OR UPDATE ON "test_textdocument" FOR EACH ROW EXECUTE PROCEDURE test_textdocument_tsv_59565b71_func();'
            ], schema_editor.deferred_sql)
