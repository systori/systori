import 'dart:html';
import 'dart:async';
import 'dart:developer';
import 'package:intl/intl.dart';
import 'common.dart';


void main() {
  Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;

  List<Element> rows = querySelectorAll('.project_row');
  double approved_total = 0.0;
  double invoiced_total = 0.0;

  for (var row in rows) {
    int id = row.dataset['project-id'];
    approved_total += parse_currency(row.querySelector('.approved_total').dataset['approved-total']);
    invoiced_total += parse_currency(row.querySelector('.invoiced_total').dataset['invoiced-total']);
  }
  querySelector('#approved_total').text = CURRENCY.format(approved_total);
  querySelector('#invoiced_total').text = CURRENCY.format(invoiced_total);
}