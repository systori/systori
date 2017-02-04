@TestOn('browser')
import 'dart:html';
import 'dart:async';
import 'package:test/test.dart';
import 'package:systori/editor.dart';
import 'tools.dart';


List findHeaders(String expression) {
    var headers = [];
    querySelectorAll(expression).forEach((g) {
        Group group = g.parent.parent;
        headers.add([group.name.text, g.style.top]);
    });
    return headers;
}


expectHeader(List<List<String>> fixed, [List<List<String>> sliding = const []]) async {
    await new Future.delayed(new Duration(milliseconds: 100));
    expect(findHeaders('.sticky-header:not(.sliding)'), fixed);
    expect(findHeaders('.sliding'), sliding);
}


void main() {
    registerElements();
    Scaffolding scaffold = new Scaffolding(querySelector('#editor-area'));
    Job job;

    setUp(() {
        scaffold.reset();
        job = Job.JOB;
        /* unit test runner doesn't provide access to /static/
           which means there is no bootstrap css to make the
           top header, instead we change the scroll to where
           the screen would normally be had there been css
           with css present the distance between the top of
           #editor-area and top of window is 70px
         */
        window.scrollTo(0, querySelector('#editor-area').offsetTop-70);
    });

    group("Sticky Header", () {

        test("enter & exit job", () async {
            window.scrollBy(0, 90);
            await expectHeader([['Big Job', '51px']]);
            window.scrollBy(0, -90);
            await expectHeader([]);
        });

        test("stack", () async {
            window.scrollBy(0, 90);
            await expectHeader([
                ['Big Job', '51px']
            ]);
            window.scrollBy(0, 90);
            await expectHeader([
                ['Big Job', '51px'],
                ['Main Group A1', '75px'],
            ]);
            window.scrollBy(0, 90);
            await expectHeader([
                ['Big Job', '51px'],
                ['Main Group A1', '75px'],
                ['Group A2.1', '99px'],
            ]);
        });

        test("slide", () async {
            Task task = job.children[1].children[2].children[2].children[2].children[1];
            window.scrollBy(0, task.getBoundingClientRect().top);
            window.scrollBy(0, 74);
            await expectHeader([
                ['Big Job', '51px'],
                ['Main Group A1', '75px'],
                ['Group A2.2', '99px'],
                ['Group A3.2', '123px'],
                ['Group A4.2', '147px'],
            ]);
            window.scrollBy(0, 3);
            await expectHeader(
                [['Big Job', '51px']],
                [['Main Group A1', '74px'],
                ['Group A2.2', '99px'],
                ['Group A3.2', '124px'],
                ['Group A4.2', '149px']]
            );
            window.scrollBy(0, 25);
            await expectHeader(
                [['Big Job', '51px']],
                [['Main Group A1', '49px'],
                ['Group A2.2', '74px'],
                ['Group A3.2', '99px'],
                ['Group A4.2', '124px']]
            );
            window.scrollBy(0, 100);
            await expectHeader([
                ['Big Job', '51px'],
                ['Main Group B1', '75px'],
            ]);
            window.scrollBy(0, -50);
            await expectHeader(
                [['Big Job', '51px']],
                [['Main Group A1', '-1px'],
                ['Group A2.2', '24px'],
                ['Group A3.2', '49px'],
                ['Group A4.2', '74px']]
            );
        });

    });

}
