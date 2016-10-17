import 'package:intl/intl.dart';


make_currency_format() => new NumberFormat("#,###,###,##0.00#");
NumberFormat CURRENCY = make_currency_format();
make_decimal_format() => new NumberFormat("#,###,###,##0.####");
NumberFormat DECIMAL = make_decimal_format();

double parse_currency(String value) => value.length > 0 ? CURRENCY.parse(value) : 0.0;

double parse_decimal(String value) => value.length > 0 ? DECIMAL.parse(value) : 0.0;

NumberFormat AMOUNT = new NumberFormat("#,###,###,##0.00");

int amount_string_to_int(String amount) =>
    (parse_currency(amount) * 100).round();

String amount_int_to_string(int amount) =>
    AMOUNT.format(amount / 100);

int string_to_int(String amount) =>
    amount.length > 0 ? (CURRENCY.parse(amount)*100).round() : null;
