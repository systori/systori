import 'dart:html';
import 'dart:math' as math;
import 'package:quiver/iterables.dart';
import 'editor.dart';


class StickyHeader {

    Job job;

    static final bool DEBUG = false;
    static final int TOP = 52;
    List<Group> oldFixedStack = [];
    List<Group> oldSlidingStack = [];
    DivElement ts, bs;

    StickyHeader(this.job) {
        window.onScroll.listen(handleScroll);
        if (DEBUG) {
            ts = document.createElement('div');
            ts.style.backgroundColor = 'green';
            bs = document.createElement('div');
            bs.style.backgroundColor = 'red';
            for (var s in [ts, bs]) {
                s.style.position = 'fixed';
                s.style.width = '1px';
                s.style.height = '2px';
                s.style.zIndex = '1000';
                job.append(s);
            }
            updateSensorMarkers();
        }
    }

    updateSensorMarkers([int bottom]) {
        if (DEBUG) {
            ts.style.top = '${TOP}px';
            ts.style.left = '${job.offsetLeft - 2}px';
            bs.style.left = '${job.offsetLeft - 2}px';
            if (bottom != null)
                bs.style.top = '${bottom}px';
            else
                bs.style.top = '0px';
        }
    }

    int stackHeight(List<Group> stack) {
        var height = 0;
        for (var model in stack) {
            height += model.children[0].children[0].clientHeight;
        }
        return height;
    }

    handleScroll(Event e) {

        if (DEBUG) print(''.padRight(10, '-'));

        Element topElement = document.elementFromPoint(job.offsetLeft, TOP);
        Group topGroup = findGroup(topElement);
        if (topGroup == null) {
            /* short circuit */
            drawStacks([], []);
            updateSensorMarkers();
            if (DEBUG) {
                print("Clearing header.");
                print("".padRight(10, '+'));
            }
            return;
        }

        List<Group> topStack = makeGroupStack(topGroup);
        var topStackHeight = stackHeight(topStack);

        if (DEBUG) print('Top Sensor: ${topGroup.name.text}');

        var middleSensor = (topStackHeight/2).round() + TOP;
        Element middleElement = document.elementFromPoint(job.offsetLeft, middleSensor);
        Group middleGroup = topElement == middleElement ? topGroup : findGroup(middleElement);

        var bottomSensor = topStackHeight + TOP;
        Element bottomElement = document.elementFromPoint(job.offsetLeft, bottomSensor);
        Group bottomGroup = middleElement == bottomElement ? middleGroup : findGroup(bottomElement);

        if (DEBUG) print('Btm Sensor: ${bottomGroup?.name?.text}');

        if (topGroup == bottomGroup || (topGroup == middleGroup && bottomGroup == null)) {
            // If top and bottom (or middle) sensors both see the same thing,
            // just drawing the topStack as a fixed header without any further
            // processing or merging.
            if (DEBUG) {
                print('Top: ${topStack.map((g)=>g.name.text).toList()}');
                print('top == bottom');
            }
            drawStacks(topStack, []);
            updateSensorMarkers(bottomSensor);
        } else if (middleGroup != topGroup && middleGroup != bottomGroup) {
            // If the middle sensor found a distinct group then make that the new
            // top.
            if (DEBUG) print('using middle group as top');
            processStack(makeGroupStack(middleGroup));
        } else if (topGroup == bottomGroup.parent) {
            // If bottom group is a child of the top group then optimistically
            // make the bottomGroup the new top.
            if (DEBUG) print('using bottom group as top');
            processStack(makeGroupStack(bottomGroup));
        } else {
            // No special cases found, just process the top stack.
            if (DEBUG) print('using top group');
            processStack(topStack, bottomGroup);
        }

        if (DEBUG) print("".padRight(10, '+'));
    }

    processStack(List<Group> topStack, [Group bottomGroup]) {

        int bottomSensor = stackHeight(topStack) + TOP;
        if (bottomGroup == null) {
            bottomGroup = findGroup(document.elementFromPoint(job.offsetLeft, bottomSensor));
        }
        List<Group> bottomStack = makeGroupStack(bottomGroup);
        List<Group> fixed = [], sliding = [];

        mergeStacks(topStack, bottomStack, fixed, sliding);

        if (DEBUG) {
            print('Top: ${topStack.map((g)=>g.name.text).toList()}');
            print('Btm: ${bottomStack.map((g)=>g.name.text).toList()}');
            print('Fixed: ${fixed.map((g)=>g.name.text).toList()}');
            print('Slide: ${sliding.map((g)=>g.name.text).toList()}');
        }

        int slidingStart;
        if (sliding.isNotEmpty) {
            var fixedBottom = fixed.last.children[0].children[0]
                .getBoundingClientRect()
                .bottom;
            var rec = bottomGroup.children[0].getBoundingClientRect();
            slidingStart = rec.top.round() - 1;
            if (fixedBottom >= slidingStart) {
                if (DEBUG) print('fixed = bottomStack');
                fixed = bottomStack;
            }
        }

        drawStacks(fixed, sliding, slidingStart);
        updateSensorMarkers(bottomSensor);

    }

    mergeStacks(List<Group> topStack, List<Group> bottomStack, List<Group> fixed, List<Group> sliding) {
        var longest = math.max(topStack.length, bottomStack.length);
        for (int i = 0; i < longest; i++) {
            var topModel = i < topStack.length ? topStack[i] : null;
            var bottomModel = i < bottomStack.length ? bottomStack[i] : null;
            if (topModel == bottomModel) {
                fixed.add(topModel);
            } else {
                if (topModel != null) {
                    sliding.insert(0, topModel);
                } else if (bottomModel != null) {
                    fixed.add(bottomModel);
                }
            }
        }
    }

    drawStacks(List<Group> newFixedStack, List<Group> newSlidingStack, [int slidingStart]) {

        for (var group in concat([oldFixedStack, oldSlidingStack])) {
            if (!newFixedStack.contains(group) && !newSlidingStack.contains(group)) {
                var editor = group.children[0];
                var row = editor.children[0];
                if (row.classes.contains('sticky-header')) {
                    row.style.top = null;
                    row.style.width = null;
                    row.classes.remove('sticky-header');
                    editor.children.removeAt(1);
                    if (DEBUG) print('"${group.name.text}".removeAt(1)');
                    row.classes.remove('sliding');
                }
            }
        }

        for (var group in concat([newFixedStack, newSlidingStack])) {
            var editor = group.children[0];
            var row = editor.children[0];
            if (!row.classes.contains('sticky-header')) {
                if (DEBUG) print('"${group.name.text}".insertBefore(document.createElement(div), ...)');
                var spacer = document.createElement('div');
                spacer.style.height = '${row.clientHeight}px';
                row.style.width = '${row.clientWidth}px';
                row.classes.add('sticky-header');
                editor.insertBefore(spacer, editor.children[1]);
            }
        }

        var offset = TOP - 1;
        for (var model in newFixedStack) {
            var editor = model.children[0];
            var row = editor.children[0];
            row.style.top = '${offset}px';
            offset += row.clientHeight - 1;
            row.classes.toggle('sliding', false);
        }

        for (var model in newSlidingStack) {
            var editor = model.children[0];
            var row = editor.children[0];
            slidingStart -= row.clientHeight;
            row.style.top = '${slidingStart}px';
            row.classes.toggle('sliding', true);
        }

        oldFixedStack = newFixedStack;
        oldSlidingStack = newSlidingStack;
    }

    Group findGroup(Element element) {
        while (element != null) {
            if (element is Group) {
                return element;
            }
            element = element.parent;
        }
        return null;
    }

    List<Group> makeGroupStack(Group group) {
        List<Group> newStack = [];
        if (group != null) {
            newStack.insert(0, group);
            while (group != null && group is! Job) {
                group = group.parent;
                if (group is Group) {
                    newStack.insert(0, group);
                }
            }
        }
        return newStack;
    }
}
