import 'package:test/test.dart';
import 'package:systori/spreadsheet.dart' show solve;


main() async {

    group("equation", () {

        test("solve", () {
            expect(solve(" 16.0 / (5-3) ").decimal, 8.0);
        });

    });

}