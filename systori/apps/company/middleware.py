import re

from django.contrib import messages
from django.db import ProgrammingError
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from boardinghouse.schema import (
    TemplateSchemaActivation, Forbidden,
    get_schema_model,
    activate_schema, deactivate_schema,
)
from boardinghouse.signals import session_requesting_schema_change, session_schema_changed


def change_schema(request, schema):
    """
    Change the schema for the current request's session.

    Note this does not actually _activate_ the schema, it only stores
    the schema name in the current request's session.
    """
    session = request.session
    user = request.user

    # Allow clearing out the current schema.
    if not schema:
        session.pop('company', None)
        return

    # Anonymous users may not select a schema.
    # Should this be selectable?
    if user.is_anonymous():
        session.pop('company', None)
        raise Forbidden()

    # We actually want the schema name, so we can see if we
    # don't actually need to change the schema at all (if the
    # session is already set, then we assume that it's all good)
    if isinstance(schema, str):
        schema_name = schema
    else:
        schema_name = schema.schema

    # Don't allow anyone, even superusers, to select the template schema.
    if schema_name == '__template__':
        raise TemplateSchemaActivation()

    # If the schema is already set to this name for this session, then
    # we can just exit early, saving some db access.
    if schema_name == session.get('company', None):
        return

    Schema = get_schema_model()

    if user.is_superuser or user.is_staff:
        # Just a sanity check: that the schema actually
        # exists at all, when the superuser attempts to set
        # the schema.
        if schema_name == schema:
            try:
                schema = Schema.objects.get(schema=schema_name)
            except Schema.DoesNotExist:
                raise Forbidden()
    else:
        # If we were passed in a schema object, rather than a string,
        # then we can check to see if that schema is active before
        # having to hit the database.
        if isinstance(schema, Schema):
            # I'm not sure that it's logically possible to get this
            # line to return True - we only pass in data from user.visible_schemata,
            # which excludes inactives.
            if not schema.is_active:
                raise Forbidden()
        # Ensure that this user has access to this schema,
        # and that this schema is active. We can do this using the
        # cache, which prevents hitting the database.
        visible_schemata = [schema.schema for schema in user.visible_companies]
        if schema_name not in visible_schemata:
            raise Forbidden()

    # Allow 3rd-party applications to listen for an attempt to change
    # the schema for a user/session, and prevent it from occurring by
    # raising an exception. We will just pass that exception up the
    # call stack.
    session_requesting_schema_change.send(
        sender=request,
        schema=schema_name,
        user=request.user,
        session=request.session,
    )
    # Actually set the schema on the session.
    session['company'] = schema_name
    # Allow 3rd-party applications to listen for a change, and act upon
    # it accordingly.
    session_schema_changed.send(
        sender=request,
        schema=schema_name,
        user=request.user,
        session=request.session,
    )


class CompanyMiddleware:
    """
    Middleware to set the postgres schema for the current request's session.

    The schema that will be used is stored in the session. A lookup will
    occur (but this could easily be cached) on each request.

    There are three ways to change the schema as part of a request.

    1. Request a page with a querystring containg a ``__schema`` value::

        https://example.com/page/?__schema=<schema-name>

      The schema will be changed (or cleared, if this user cannot view
      that schema), and the page will be re-loaded (if it was a GET). This
      method of changing schema allows you to have a link that changes the
      current schema and then loads the data with the new schema active.

      It is used within the admin for having a link to data from an
      arbitrary schema in the ``LogEntry`` history.

      This type of schema change request should not be done with a POST
      request.

    2. Add a request header::

        X-Change-Schema: <schema-name>

      This will not cause a redirect to the same page without query string. It
      is the only way to do a schema change within a POST request, but could
      be used for any request type.

    3. Use a specific request::

        https://example.com/__change_schema__/<schema-name>/

      This is designed to be used from AJAX requests, or as part of
      an API call, as it returns a status code (and a short message)
      about the schema change request. If you were storing local data,
      and did one of these, you are probably going to have to invalidate
      much of that.

    You could also come up with other methods.

    """

    def process_request(self, request):
        FORBIDDEN = HttpResponseForbidden(_('You may not select that schema'))
        # Ways of changing the schema.
        # 1. URL /__change_schema__/<name>/
        # This will return a whole page.
        # We don't need to activate, that happens on the next request.
        if request.path.startswith('/__change_schema__/'):
            schema = request.path.split('/')[2]
            try:
                change_schema(request, schema)
            except Forbidden:
                return FORBIDDEN

            if 'company' in request.session:
                response = _('Company changed to %s') % request.session['company']
            else:
                response = _('Company deselected')

            return HttpResponse(response)

        # 2. GET querystring ...?__schema=<name>
        # This will change the query, and then redirect to the page
        # without the schema name included.
        elif request.GET.get('__schema', None) is not None:
            schema = request.GET['__schema']
            try:
                change_schema(request, schema)
            except Forbidden:
                return FORBIDDEN

            data = request.GET.copy()
            data.pop('__schema')

            if request.method == "GET":
                # redirect so we strip the schema out of the querystring.
                if data:
                    return redirect(request.path + '?' + data.urlencode())
                return redirect(request.path)

            # method == 'POST' or other
            request.GET = data

        # 3. Header "X-Change-Schema: <name>"
        elif 'HTTP_X_CHANGE_SCHEMA' in request.META:
            schema = request.META['HTTP_X_CHANGE_SCHEMA']
            try:
                change_schema(request, schema)
            except Forbidden:
                return FORBIDDEN

        elif 'company' not in request.session and len(request.user.visible_companies):
            # Can we not require a db hit each request here?
            change_schema(request, request.user.visible_companies[0])

        if 'company' in request.session:
            activate_schema(request.session['company'])
        else:
            deactivate_schema()

    def process_template_response(self, request, response):
        if hasattr(response, 'context_data'):

            if 'companies' not in response.context_data and not request.user.is_anonymous():
                response.context_data['companies'] = request.user.visible_companies

            if 'company' not in response.context_data and not request.user.is_anonymous():
                Schema = get_schema_model()
                response.context_data['company'] = Schema.objects.get(schema=request.session.get('company'))

        return response

    def process_exception(self, request, exception):
        """
        In the case a request returned a DatabaseError, and there was no
        schema set on ``request.session``, then look and see if the error
        that was provided by the database may indicate that we should have
        been looking inside a schema.

        In the case we had a :class:`TemplateSchemaActivation` exception,
        then we want to remove that key from the session.
        """
        if isinstance(exception, ProgrammingError) and not request.session.get('company'):
            if re.search('relation ".*" does not exist', exception.args[0]):
                # I'm not sure if this should be done or not, but it does
                # fail without the if statement from django 1.8+
                # if not transaction.get_autocommit():
                #     transaction.rollback()

                # Should we return an error, or redirect? When should we
                # do one or the other? For an API, we would want an error
                # but for a regular user, a redirect may be better.

                # Can we see if there is already a pending message for this
                # request that has the same content as us?
                messages.error(request,
                               _("You must select a schema to access that resource"),
                               fail_silently=True
                               )
                return HttpResponseRedirect('..')
        # I'm not sure we ever really hit this one, but it's worth keeping
        # here just in case we've missed something.
        if isinstance(exception, TemplateSchemaActivation):
            request.session.pop('company', None)
            return HttpResponseForbidden(_('You may not select that company'))
