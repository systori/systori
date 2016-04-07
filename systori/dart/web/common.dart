import 'package:intl/intl.dart';


NumberFormat CURRENCY = new NumberFormat("#,###,###,##0.00#");
NumberFormat DECIMAL = new NumberFormat("#,###,###,##0.####");

double parse_currency(String value) => value.length > 0 ? CURRENCY.parse(value) : 0.0;

double parse_decimal(String value) => value.length > 0 ? DECIMAL.parse(value) : 0.0;
