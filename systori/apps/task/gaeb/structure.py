from django.db import models
from django.core import exceptions, validators
from django.forms import forms
from django.utils.translation import ugettext_lazy as _


class GAEBStructure:
    """ See: docs/GAEB_DA_XML_3.0_en.pdf
        Dart version: dart/lib/src/editor/gaeb.dart
    """

    MAXLEVELS = 6  # 1 Lot/Job + 4 Categories + 1 Task

    def __init__(self, pattern):

        if not pattern:
            raise exceptions.ValidationError(
                "GAEB hierarchy cannot be blank.", code="invalid"
            )

        self.pattern = pattern
        self.zfill = [len(p) for p in pattern.split(".")]

        if not (2 <= len(self.zfill) <= self.MAXLEVELS):
            raise exceptions.ValidationError(
                "GAEB hierarchy is outside the allowed hierarchy depth.", code="invalid"
            )

    def __str__(self):
        return self.pattern

    @property
    def maximum_depth(self):
        return len(self.zfill) - 2

    @staticmethod
    def _format(position, zfill):
        return str(position).zfill(zfill)

    def format_task(self, position):
        return self._format(position, self.zfill[-1])

    def format_group(self, position, depth):
        assert self.is_valid_depth(
            depth
        ), "Group depth is beyond the allowed structure depth."
        return self._format(position, self.zfill[depth])

    def is_valid_depth(self, depth):
        return 0 <= depth <= self.maximum_depth


class GAEBStructureFormField(forms.Field):
    def __init__(self, max_length=None, *args, **kwargs):
        self.max_length = max_length
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, GAEBStructure) or value is None:
            return value
        return GAEBStructure(value)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs["maxlength"] = self.max_length
        return attrs


class GAEBStructureProperty:
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, type=None):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if isinstance(value, str):
            value = GAEBStructure(value)
        if isinstance(value, GAEBStructure):
            instance.__dict__[self.name] = value
            instance.__dict__[self.name + "_depth"] = value.maximum_depth
        else:
            raise TypeError(
                "%s value must be a GAEBStructure instance, not '%r'"
                % (self.name, value)
            )


class GAEBStructureField(models.Field):
    description = _("Pattern for the GAEB hierarchy code structure.")

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 64
        self.structure_dept = not kwargs.pop("structure_depth", False)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        kwargs["structure_depth"] = True
        return name, path, args, kwargs

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name)
        depth_name = name + "_depth"

        setattr(cls, name, GAEBStructureProperty(name))  # maybe not needed?

        if self.structure_dept and not cls._meta.abstract:
            structure_depth = models.PositiveIntegerField(editable=False, db_index=True)
            cls.add_to_class(depth_name, structure_depth)

        setattr(
            cls,
            depth_name,
            property(
                fget=lambda obj: obj.__dict__[depth_name], fset=lambda obj, val: None
            ),
        )  # maybe not needed?

    def get_internal_type(self):
        return "CharField"

    @staticmethod
    def from_db_value(value, expression, connection):
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
        return value.pattern

    def formfield(self, **kwargs):
        defaults = {"form_class": GAEBStructureFormField, "max_length": self.max_length}
        defaults.update(kwargs)
        return super().formfield(**defaults)
