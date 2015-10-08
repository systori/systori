import 'dart:html';
import 'package:intl/intl.dart';
import 'common.dart';


NumberFormat AMOUNT = new NumberFormat("#,###,###,##0.00");

void main() {
    Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;

    InputElement amount_input = querySelector('input[name="amount"]');
    CheckboxInputElement is_tax_included_input = querySelector('input[name="is_tax_included"]');
    TableCellElement gross_amount = querySelector('td[id="gross-amount"]');
    TableCellElement net_amount = querySelector('td[id="net-amount"]');
    TableCellElement tax_amount = querySelector('td[id="tax-amount"]');
    double TAX_RATE = parse_decimal(tax_amount.dataset['tax-rate']);

    var update_table = (e) {
        // this should always match the Python implementation in apps/document/type/invoice.py
        double amount = parse_decimal(amount_input.value);
        if (is_tax_included_input.checked) {
            double net = amount / (1 + TAX_RATE);
            gross_amount.text = AMOUNT.format(amount);
            net_amount.text = AMOUNT.format(net);
            tax_amount.text = AMOUNT.format(amount-net);
        } else {
            double tax = amount * TAX_RATE;
            gross_amount.text = AMOUNT.format(amount+tax);
            net_amount.text = AMOUNT.format(amount);
            tax_amount.text = AMOUNT.format(tax);
        }
    };

    update_table(null);
    amount_input.onKeyUp.listen(update_table);
    is_tax_included_input.onChange.listen(update_table);
}
