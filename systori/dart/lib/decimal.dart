import 'package:intl/intl.dart';


Decimal sum(Iterable<Decimal> decimals) => decimals.reduce((i, j) => i + j);


makeNumberFormat() => new NumberFormat("#,###,###,##0.####");
makeMoneyFormat() => new NumberFormat("#,###,###,##0.00");


class Decimal {

    static NumberFormat MONEY = makeMoneyFormat();
    static NumberFormat NUMBER = makeNumberFormat();
    static updateFormats() {
        MONEY = makeMoneyFormat();
        NUMBER = makeNumberFormat();
    }

    static final RegExp NUMBER_STUFF = new RegExp(r'^-?[0-9.,]+$');
    static bool isNullBlankOrNumber(String text) {
        if (text == null || text == "")
            return true;
        var trimmed = text.trim();
        if (trimmed == "" || NUMBER_STUFF.hasMatch(trimmed))
            return true;
        return false;
    }

    final int _decimal;
    final int _precision;

    bool get isNull => _decimal == null;
    bool get isNotNull => _decimal != null;
    bool get isZero => _decimal == 0;
    bool get isNonzero => isNotNull && !isZero;
    double get decimal => isNull ? _decimal : _decimal / _precision;
    String get money => MONEY.format(decimal);
    String get number => NUMBER.format(decimal);

    Decimal([num number=0, precision=1000]):
            this._(number != null ? (number * precision).round() : number, precision);

    Decimal.parse(String value):
            this(value != null && value.length > 0 ? NUMBER.parse(value) : null);

    Decimal._(this._decimal, this._precision);

    Decimal operator * (Decimal other) =>
        new Decimal._(((_decimal * other._decimal) / _precision).round(), _precision);

    Decimal operator / (Decimal other) =>
        new Decimal._(((_decimal / other._decimal) * _precision).round(), _precision);

    Decimal operator - (Decimal other) =>
        new Decimal._(_decimal - other._decimal, _precision);

    Decimal operator + (Decimal other) =>
        new Decimal._(_decimal + other._decimal, _precision);

    bool operator < (Decimal other) =>
        _decimal < other._decimal;

    bool operator <= (Decimal other) =>
        _decimal <= other._decimal;

    bool operator > (Decimal other) =>
        _decimal > other._decimal;

    bool operator >= (Decimal other) =>
        _decimal >= other._decimal;
}
