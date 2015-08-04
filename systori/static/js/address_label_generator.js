$(function () {
    var input_fields = [
        'business',
        'salutation',
        'first_name',
        'last_name',
        'address',
        'postal_code',
        'city'
    ];
    for (var i in input_fields) input_fields[i] = '#id_'+input_fields[i];
    var selector = input_fields.join(',');

    function update_address_label() {
        $('#id_address_label').val(

            $('#id_business').val() + "\n" +

            "z.H. " + $('#id_salutation').val() + " " +
            $('#id_first_name').val() + " " + $('#id_last_name').val() + "\n" +

            $('#id_address').val() + "\n" +
            $('#id_postal_code').val() + " "  + $('#id_city').val() + "\n"
        );
    }

    function enable_automatic() {
        $('#id_address_label').prop('readonly', true);
        $(selector).on('keyup', update_address_label);
        update_address_label();
    }

    function disable_automatic() {
        $('#id_address_label').prop('readonly', false);
        $(selector).off('keyup', update_address_label);
    }

    if ($('#id_is_address_label_generated').is(":checked")) {
        enable_automatic();
    }

    $('#id_is_address_label_generated').click(function() {
        if (this.checked) {
            enable_automatic();
        } else {
            disable_automatic();
        }
    })

});
