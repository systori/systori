from django.db import models


def update_instance(instance, data, model_to_json_mapping=None):
    for name, value in data.items():
        try:
            field = instance._meta.get_field(name)
            field.save_form_data(instance, value)
        except models.FieldDoesNotExist:
            instance.json[name] = value

    if model_to_json_mapping:
        for model_field, json_field in model_to_json_mapping.items():
            instance.json[json_field] = data[model_field]

    return instance
