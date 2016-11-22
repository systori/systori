import 'dart:html';
import 'package:test/test.dart';
import '../web/job_editor.dart';
import '../web/job_editor.dart' as job_editor;

void main() { job_editor.main();

    group("Job", () {

        test("pk set", () {
            JobElement job = querySelector("sys-job");
            expect(job.pk, equals(1));
        });

    });
}
