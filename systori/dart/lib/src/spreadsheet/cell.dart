import 'package:systori/decimal.dart';
import 'spreadsheet.dart';
import 'range.dart';
import 'equation.dart';


abstract class Cell {

    Decimal get value;
    set value(Decimal value);

    String get rawEquation;

    set resolvedEquation(String equation);
    String get resolvedEquation;

    int get column;
    List<Range> ranges;
    Map<String,Decimal> cache = {};
    bool isPrimed = false;

    bool get hasEquation => rawEquation.isNotEmpty;

    equationChanged(Spreadsheet sheet) {
        if (!hasEquation) {
            resolvedEquation = "";
            ranges = [];
            return;
        }
        ranges = Range.extractRanges(rawEquation);
        calculate(sheet);
        isPrimed = true;
    }

    dependenciesChanged(Spreadsheet sheet) {
        if (!hasEquation) return;
        if (!isPrimed && hasEquation) {
            ranges = Range.extractRanges(rawEquation);
            isPrimed = true;
        }
        cache = {};
        calculate(sheet);
    }

    calculate(Spreadsheet sheet) {
        updateCache(sheet);
        resolvedEquation = Range.resolveRanges(rawEquation, ranges, cache);
        value = solve(resolvedEquation);
    }

    updateCache(Spreadsheet sheet) {
        for (var range in ranges) {
            var columnIdx = range.column!=null ? range.column : column;
            cache.putIfAbsent(range.src, ()=>
                range.calculate(sheet.getColumn(columnIdx).toList())
            );
        }
    }

    List<List<int>> rangeMatrix;

    updateRangeMatrix(int rows) {
        rangeMatrix = new List.generate(rows, (i)=>[0,0,0]);
        for (var range in ranges) {
            for (int row = 0; row < rangeMatrix.length; row++) {
                if (range.isHit(row)) {
                    var col = range.column != null ? range.column : column;
                    if (rangeMatrix[row][col] != 0) {
                        rangeMatrix[row][col] = -1;
                    } else {
                        rangeMatrix[row][col] = range.group;
                    }
                }
            }
        }
    }
}


