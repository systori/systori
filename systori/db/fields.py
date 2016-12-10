from django.core import checks
from django.contrib.postgres.search import SearchVectorField
from django.utils.translation import ugettext_lazy as _


class TSVector:

    def __init__(self, name, weight):
        assert isinstance(name, str)
        assert weight in ('A', 'B', 'C', 'D')
        self.name = name
        self.weight = weight

    def deconstruct(self):
        path = "%s.%s" % (self.__class__.__module__, self.__class__.__name__)
        return path, [self.name, self.weight], {}


class TSVectorField(SearchVectorField):
    description = _("PostgreSQL tsvector type field.")

    def __init__(self, columns, language, *args, **kwargs):
        self.columns = columns
        self.language = language
        kwargs['db_index'] = True
        kwargs['null'] = True
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['columns'] = self.columns
        kwargs['language'] = self.language
        del kwargs['db_index']
        del kwargs['null']
        return name, path, args, kwargs

    def check(self, **kwargs):
        errors = super().check(**kwargs)
        errors.extend(self._check_columns_attribute(**kwargs))
        errors.extend(self._check_language_attribute(**kwargs))
        return errors

    def _check_columns_attribute(self, **kwargs):
        if self.columns is None:
            return [
                checks.Error(
                    "TSVectorField must define a 'columns' attribute.",
                    obj=self,
                    id='fields.E401',
                )
            ]
        elif not isinstance(self.columns, (list, tuple)) or not all(isinstance(tsv, TSVector) for tsv in self.columns):
            return [
                checks.Error(
                    "'columns' must be a list or tuple of TSVector instances.",
                    obj=self,
                    id='fields.E402',
                )
            ]
        else:
            return []

    def _check_language_attribute(self, **kwargs):
        if self.language is None:
            return [
                checks.Error(
                    "TSVectorField must define a 'language' attribute.",
                    obj=self,
                    id='fields.E403',
                )
            ]
        elif not isinstance(self.language, str):
            return [
                checks.Error(
                    "'language' must be a string.",
                    obj=self,
                    id='fields.E404',
                )
            ]
        else:
            return []
