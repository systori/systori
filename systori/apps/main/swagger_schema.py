"""
    Custom swagger schema modifications
"""
from drf_yasg.inspectors import view
from drf_yasg import openapi
from drf_yasg.errors import SwaggerGenerationError
from drf_yasg.utils import merge_params
from rest_framework.request import is_form_media_type


class SwaggerSchema(view.SwaggerAutoSchema):
    """
    Custom swagger schema modifications
    """

    def add_manual_parameters(self, parameters):
        """Add/replace parameters from the given list of automatically generated request parameters.

        :param list[openapi.Parameter] parameters: genereated parameters
        :return: modified parameters
        :rtype: list[openapi.Parameter]
        """
        manual_parameters = self.overrides.get("manual_parameters", None) or []
        auto_include_parameters = self.overrides.get("auto_include_parameters", True)

        body_schema_at_wrong_place = any(
            param.in_ == openapi.IN_BODY for param in manual_parameters
        )
        if body_schema_at_wrong_place:  # pragma: no cover
            raise SwaggerGenerationError(
                "specify the body parameter as a Schema or Serializer in request_body"
            )

        has_manual_form_parameter = any(
            param.in_ == openapi.IN_FORM for param in manual_parameters
        )
        if has_manual_form_parameter:  # pragma: no cover
            has_body_parameter = any(
                param.in_ == openapi.IN_BODY for param in parameters
            )
            has_correct_consumes = any(
                is_form_media_type(encoding) for encoding in self.get_consumes()
            )

            # A manual form parameter is invalid when
            # 1. The parent operation accepts body parameter
            # 2. The parent operation does not consume form data or multipart form data
            has_invalid_parameter = auto_include_parameters and (
                has_body_parameter or not has_correct_consumes
            )
            if has_invalid_parameter:

                raise SwaggerGenerationError(
                    "cannot add form parameters when the request has a request body; "
                    "did you forget to set an appropriate parser class on the view?"
                )
            if self.method not in self.body_methods:
                raise SwaggerGenerationError(
                    "form parameters can only be applied to "
                    "(" + ",".join(self.body_methods) + ") HTTP methods"
                )

        return (
            merge_params(parameters, manual_parameters)
            if auto_include_parameters
            else manual_parameters
        )

    def get_produces(self):
        """
        Returns the MIME type this operation produces. 
        Allows overriding it using swagger_auto_schema decorator
        """
        produces = self.overrides.get("produces", None)
        if produces:
            if isinstance(produces, str):
                return [produces]
            if isinstance(produces, (list, tuple)):
                return list(produces)
        return super().get_produces()
