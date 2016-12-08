@TestOn('browser')
import 'package:test/test.dart';
import 'package:systori/editor.dart';

main() {

    group("GAEBStructureTests", () {

        test("task formatting", () {
            var struct = new GAEBHierarchyStructure("9.01.02.0009");
            expect(struct.formatTask('1'), '0001');
            expect(struct.formatTask('12345'), '12345');
        });

        test("group formatting", () {
            var struct = new GAEBHierarchyStructure("9.000.00.0000");
            expect(struct.formatGroup('1', 0), '1');
            expect(struct.formatGroup('99', 1), '099');
            expect(struct.formatGroup('99', 2), '99');
        });

        test("isValidDepth check", () {
            var struct = new GAEBHierarchyStructure("9.000.00.0000");
            expect(struct.isValidDepth(-1), false);
            expect(struct.isValidDepth(0), true);
            expect(struct.isValidDepth(1), true);
            expect(struct.isValidDepth(2), true);
            expect(struct.isValidDepth(3), false);
            expect(struct.isValidDepth(4), false);
        });

        test("depth", () {
            var gaeb = (s)=>new GAEBHierarchyStructure(s);
            expect(gaeb('0.0').maximum_depth, 0);
            expect(gaeb('0.0.0').maximum_depth, 1);
            expect(gaeb('0.0.0.0').maximum_depth, 2);
        });

    });

}

