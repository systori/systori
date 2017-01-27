import 'package:intl/intl.dart';


Decimal sum(Iterable<Decimal> decimals) => decimals.reduce((i, j) => i + j);


makeNumberFormat() => new NumberFormat("#,###,###,##0.####");
makeMoneyFormat() => new NumberFormat("#,###,###,##0.00#");
makeDifferenceFormat() => new NumberFormat("+#,###,###,##0.00#;-#,###,###,##0.00#");


class Decimal implements Comparable<Decimal> {

    static NumberFormat MONEY = makeMoneyFormat();
    static NumberFormat NUMBER = makeNumberFormat();
    static NumberFormat DIFFERENCE = makeDifferenceFormat();
    static NumberFormat CANONICAL = new NumberFormat("0.####", "en");
    static updateFormats() {
        MONEY = makeMoneyFormat();
        NUMBER = makeNumberFormat();
        DIFFERENCE = makeDifferenceFormat();
    }

    final int _decimal;
    final int _precision;

    bool get isNull => _decimal == null;
    bool get isNotNull => !isNull;
    bool get isZero => _decimal == 0;
    bool get isNonzero => isNotNull && !isZero;

    double get decimal => isNull ? _decimal : _decimal / _precision;
    String get money => isNull ? "" : MONEY.format(decimal);
    String get number => isNull ? "" : NUMBER.format(decimal);
    String get difference => isNull ? "" : DIFFERENCE.format(decimal);
    String get canonical => isNull ? "" : CANONICAL.format(decimal);
    String get percent => isNull ? "" : "${(decimal*100).round()}%";

    Decimal([num number=0, int precision=1000]):
            this._(number != null ? (number * precision).round() : number, precision);

    Decimal.parse(String value):
            this(value != null && value.length > 0 ? NUMBER.parse(value) : null);

    Decimal._(this._decimal, this._precision);

    int compareTo(Decimal other) => _decimal.compareTo(other._decimal);

    String toString() => isNull ? "null" : number;

    Decimal operator * (Decimal other) =>
        new Decimal._(((_decimal * other._decimal) / _precision).round(), _precision);

    Decimal operator / (Decimal other) =>
        new Decimal._(((_decimal / other._decimal) * _precision).round(), _precision);

    Decimal operator - (Decimal other) =>
        new Decimal._(_decimal - other._decimal, _precision);

    Decimal operator + (Decimal other) =>
        new Decimal._(_decimal + other._decimal, _precision);

    bool operator == (dynamic other) =>
        other is Decimal && _decimal == other._decimal;

    bool operator < (Decimal other) =>
        _decimal < other._decimal;

    bool operator <= (Decimal other) =>
        _decimal <= other._decimal;

    bool operator > (Decimal other) =>
        _decimal > other._decimal;

    bool operator >= (Decimal other) =>
        _decimal >= other._decimal;

    int get hashCode {
        // TODO: re-implement this when dart sdk exposes _JenkinsSmiHash
        //  SEE: https://github.com/dart-lang/sdk/issues/11617
        return _decimal.hashCode ^ _precision.hashCode;
    }
}


class Amount {

    final Decimal net;
    final Decimal tax;
    Decimal get gross => net + tax;
    final Decimal tax_rate;

    Amount(this.net, this.tax, this.tax_rate);

    Amount.fromStrings(String net, String tax, String rate): this(
        new Decimal.parse(net),
        new Decimal.parse(tax),
        new Decimal.parse(rate)
    );

    Amount.fromStringsZeroBlank(String net, String tax, String rate): this.fromStrings(
        net.length > 0 ? net : '0',
        tax.length > 0 ? tax : '0',
        rate.length > 0 ? rate : '0'
    );

    Amount.from(num net, num tax, num rate): this(
        new Decimal(net),
        new Decimal(tax),
        new Decimal(rate)
    );

    factory
    Amount.fromGross(Decimal gross, Decimal tax_rate) {
        var net = gross / (new Decimal(1) + tax_rate);
        var tax = gross - net;
        return new Amount(net, tax, tax_rate);
    }

    Amount zero() =>
        new Amount(new Decimal(), new Decimal(), tax_rate);

    Amount adjustNet(Decimal new_net) =>
        new Amount(new_net, gross - new_net, tax_rate);

    Amount adjustTax(Decimal new_tax) =>
        new Amount(gross - new_tax, new_tax, tax_rate);

    Amount adjustGross(Decimal new_gross) =>
        new Amount.fromGross(new_gross, tax_rate);

    Amount zeroNegatives() =>
        new Amount(net.decimal < 0 ? new Decimal() : net, tax.decimal < 0 ? new Decimal() : tax, tax_rate);

    Amount operator * (Decimal multiple) =>
        new Amount(net * multiple, tax * multiple, tax_rate);

    Amount operator - (Amount other) =>
        new Amount(net - other.net, tax - other.tax, tax_rate);

    Amount operator + (Amount other) =>
        new Amount(net + other.net, tax + other.tax, tax_rate);

    bool operator == (dynamic other) =>
        other is Amount &&
        gross == other.gross &&
        net == other.net &&
        tax == other.tax &&
        tax_rate == other.tax_rate;

    int get hashCode {
        // TODO: re-implement this when dart sdk exposes _JenkinsSmiHash
        //  SEE: https://github.com/dart-lang/sdk/issues/11617
        return net.hashCode ^ tax.hashCode;
    }

    String toString() =>
        'Amount(gross: ${gross.money}, net: ${net.money}, tax: ${tax.money}, rate: ${tax_rate.number})';

}
