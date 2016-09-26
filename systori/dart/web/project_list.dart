import 'dart:html';
import 'dart:async';
import 'dart:developer';
//import 'package:intl/intl.dart';

final currency_us = new NumberFormat("#,##0.00", "en_US");
final currency_de = new NumberFormat("#.##0,00", "de_DE");

void main() {
//  Intl.systemLocale = (querySelector('html') as HtmlHtmlElement).lang;

  List<Element> rows = querySelectorAll('.project_row');
  double approved_total = 0.0;
  double invoiced_total = 0.0;

  for (var row in rows) {
    int id = row.dataset['project-id'];
    approved_total += double.parse(row.querySelector('.approved_total').dataset['approved-total']);
    invoiced_total += double.parse(row.querySelector('.invoiced_total').dataset['invoiced-total']);
//      approved_total += currency_de.format(row.querySelector('.approved_total').text);
//      invoiced_total += currency_de.format(row.querySelector('.invoiced_total').text);

  }
  querySelector('#approved_total').text = approved_total.toString();
  querySelector('#invoiced_total').text = invoiced_total.toString();
}