import 'dart:html';
import 'dart:math';
import 'package:systori/inputs.dart';
import 'model.dart';


enum NavDir {
    UP,
LEFT, RIGHT,
   DOWN
}


class ArrowNavigationHandler extends KeyboardHandler {

    static Map<String,Map<NavDir,String>> buildNavigationMap(List<List<String>> inputMatrix) {
        Map<String,Map<NavDir,String>> mapping = {};
        for (int rowIdx=0; rowIdx < inputMatrix.length; rowIdx++) {
            var row = inputMatrix[rowIdx];
            for (int colIdx=0; colIdx < row.length; colIdx++) {
                var input = row[colIdx];
                if (mapping.containsKey(input))
                    throw new ArgumentError('Input $input appears more than once in inputMatrix.');
                var map = mapping[input] = {};
                if (rowIdx > 0) {
                    var rowAbove = inputMatrix[rowIdx-1];
                    map[NavDir.UP] = rowAbove[min(colIdx, rowAbove.length)];
                }
                if (colIdx > 0) {
                    map[NavDir.LEFT] =  row[colIdx-1];
                }
                if ((colIdx+1) < row.length) {
                    map[NavDir.RIGHT] = row[colIdx+1];
                }
                if ((rowIdx+1) < inputMatrix.length) {
                    var rowBelow = inputMatrix[rowIdx+1];
                    if (colIdx < rowBelow.length) {
                        map[NavDir.DOWN] = rowBelow[colIdx];
                    }
                }
            }
        }
        return mapping;
    }

    Model model;
    Map<String,Map<NavDir,String>> mapping;

    ArrowNavigationHandler(this.mapping, this.model) {
        bindAll(model.inputs.values);
    }

    @override
    bool onKeyDownEvent(KeyEvent e, Input input) {
        if (e.ctrlKey && mapping.containsKey(input.name)) {
            var map = mapping[input.name];
            switch (e.keyCode) {
                case KeyCode.UP:
                    e.preventDefault();
                    if (map.containsKey(NavDir.UP)) {
                        model.inputs[map[NavDir.UP]].focus();
                        return true;
                    }
                    return focusOtherModel(model.firstAbove(), input.name);
                case KeyCode.DOWN:
                    e.preventDefault();
                    if (map.containsKey(NavDir.DOWN)) {
                        model.inputs[map[NavDir.DOWN]].focus();
                        return true;
                    }
                    return focusOtherModel(model.firstBelow(), input.name);
                case KeyCode.LEFT:
                    e.preventDefault();
                    if (map.containsKey(NavDir.LEFT)) {
                        model.inputs[map[NavDir.LEFT]].focus();
                        return true;
                    }
                    return false;
                case KeyCode.RIGHT:
                    e.preventDefault();
                    if (map.containsKey(NavDir.RIGHT)) {
                        model.inputs[map[NavDir.RIGHT]].focus();
                        return true;
                    }
                    return false;
            }
        }
        return false;
    }

    focusOtherModel(Model other, String tryInput) {
        if (other != null) {
            if (tryInput == "description" || !other.inputs.containsKey(tryInput)) {
                other.inputs['name'].focus();
            } else {
                other.inputs[tryInput].focus();
            }
            return true;
        }
        return false;
    }

}

