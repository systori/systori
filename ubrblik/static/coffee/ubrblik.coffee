$ ->
    $(".language-link").on "click", (event) ->
        event.preventDefault()
        $("input[name='language']").val($(this).data("language"))
        $(this).parents("form").submit()

