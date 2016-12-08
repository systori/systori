from django.db import models
from django.core import exceptions, validators
from django.utils.translation import ugettext_lazy as _


class GAEBStructure:
    """ See: docs/GAEB_DA_XML_3.0_en.pdf
        Dart version: dart/lib/src/editor/gaeb.dart
    """

    MAXLEVELS = 6  # 1 Lot/Job + 4 Categories + 1 Task

    def __init__(self, structure):

        if not structure:
            raise exceptions.ValidationError(
                "GAEB hierarchy cannot be blank.",
                code='invalid',
            )

        self.structure = structure
        self.zfill = [len(p) for p in structure.split('.')]

        if not (2 <= len(self.zfill) <= self.MAXLEVELS):
            raise exceptions.ValidationError(
                "GAEB hierarchy is outside the allowed hierarchy depth.",
                code='invalid',
            )

    @property
    def maximum_depth(self):
        return len(self.zfill)-2

    @staticmethod
    def _format(position, zfill):
        return str(position).zfill(zfill)

    def format_task(self, position):
        return self._format(position, self.zfill[-1])

    def format_group(self, position, depth):
        assert self.is_valid_depth(depth), "Group depth is beyond the allowed structure depth."
        return self._format(position, self.zfill[depth])

    def is_valid_depth(self, depth):
        return 0 <= depth <= self.maximum_depth


class GAEBStructureField(models.Field):
    description = _("Pattern for the GAEB hierarchy code structure.")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 256
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs

    def get_internal_type(self):
        return "CharField"

    @staticmethod
    def from_db_value(value, expression, connection, context):
        if value is None:
            return value
        return GAEBStructure(value)

    def to_python(self, value):
        if isinstance(value, GAEBStructure) or value is None:
            return value
        return GAEBStructure(value)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        value = self.to_python(value)
        return value.structure
