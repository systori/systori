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
        window.onScroll.listen(stickyHeader);
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

    stickyHeader(Event e) {
        Element topElement = document.elementFromPoint(job.offsetLeft, TOP);
        Group topGroup = findGroup(topElement);
        if (topGroup == null) {
            clearAndDrawStacks([], []);
            updateSensorMarkers();
            return;
        }
        List<Group> topStack = makeGroupStack(topGroup);
        var topStackHeight = stackHeight(topStack);

        var middleSensor = (topStackHeight/2).round() + TOP;
        Element middleElement = document.elementFromPoint(job.offsetLeft, middleSensor);
        Group middleGroup = topElement == middleElement ? topGroup : findGroup(middleElement);

        var bottomSensor = topStackHeight + TOP;
        Element bottomElement = document.elementFromPoint(job.offsetLeft, bottomSensor);
        Group bottomGroup = middleElement == bottomElement ? middleGroup : findGroup(bottomElement);

        if (topGroup == bottomGroup || bottomGroup == null) {
            clearAndDrawStacks(topStack, []);
            updateSensorMarkers(bottomSensor);
            return;
        }

        var bottomStack = makeGroupStack(bottomGroup);

        if (middleGroup != topGroup && middleGroup != bottomGroup) {
            if (middleGroup.nextElementSibling != bottomGroup) {
                bottomGroup = middleGroup;
                bottomStack = makeGroupStack(bottomGroup);
                bottomSensor = stackHeight(bottomStack) + TOP;
            }
        }

        var _bottomSensor = stackHeight(bottomStack) + TOP;
        if (_bottomSensor > bottomSensor) {
            Element _bottomElement = document.elementFromPoint(job.offsetLeft, _bottomSensor);
            Group _bottomGroup = bottomElement == _bottomElement ? bottomGroup : findGroup(_bottomElement);
            if (bottomGroup != _bottomGroup) {
                topGroup = bottomGroup;
                topStack = bottomStack;
                bottomGroup = _bottomGroup;
                bottomStack = makeGroupStack(_bottomGroup);
            }
            bottomSensor = _bottomSensor;
        }

        if (topGroup == bottomGroup.parent) {
            clearAndDrawStacks(bottomStack, []);
            updateSensorMarkers(bottomSensor);
        } else {
            List<Group> fixed = [], sliding = [];
            mergeStacks(topStack, bottomStack, fixed, sliding);
            clearStacks(fixed, sliding);
            var fixedBottom = fixed.last.children[0].children[0].getBoundingClientRect().bottom;
            var rec = bottomGroup.children[0].children[0].getBoundingClientRect();
            int slidingStart = rec.top.round() - 1;
            if (fixedBottom >= slidingStart) {
                fixed = bottomStack;
                clearStacks(fixed, sliding);
            }
            drawStacks(fixed, sliding, slidingStart);
            updateSensorMarkers(bottomSensor);
        }
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

    clearAndDrawStacks(List<Group> newFixedStack, List<Group> newSlidingStack) {
        clearStacks(newFixedStack, newSlidingStack);
        drawStacks(newFixedStack, newSlidingStack);
    }

    clearStacks(List<Group> newFixedStack, List<Group> newSlidingStack) {
        for (var group in concat([oldFixedStack, oldSlidingStack])) {
            if (!newFixedStack.contains(group) && !newSlidingStack.contains(group)) {
                var editor = group.children[0];
                var row = editor.children[0];
                if (row.classes.contains('sticky-header')) {
                    row.style.top = null;
                    row.style.width = null;
                    row.classes.remove('sticky-header');
                    row.classes.remove('sliding');
                    editor.children.removeAt(1);
                }
            }
        }
    }

    drawStacks(List<Group> newFixedStack, List<Group> newSlidingStack, [int slidingStart]) {

        for (var group in concat([newFixedStack, newSlidingStack])) {
            var editor = group.children[0];
            var row = editor.children[0];
            if (!row.classes.contains('sticky-header')) {
                editor.insertBefore(document.createElement('div'), editor.children[1]);
                editor.children[1].style.height = '${row.clientHeight}px';
                row.style.width = '${row.clientWidth}px';
                row.classes.add('sticky-header');
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
