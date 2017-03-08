def apply_all_kwargs(obj, **kwargs):
    for field in obj._meta.get_fields():
        if field.attname in kwargs:
            value = kwargs.pop(field.attname)
            setattr(obj, field.attname, value)
    if kwargs:
        raise TypeError(
            "'{}' is not a valid field of {}"
            .format(list(kwargs)[0], obj.__class__.__name__)
        )
