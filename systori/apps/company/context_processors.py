def schemata(request):
    """
    A Django context_processor that provides access to the
    logged-in user's visible schemata, and selected schema.

    Adds the following variables to the context:

        `schemata`: all available schemata this user has

        `selected_schema`: the currenly selected schema name

    """
    if request.user.is_anonymous():
        return {}

    return {
        'companies': request.user.visible_companies,
        'company': request.session.get('company', None)
    }
