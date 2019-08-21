/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = "./src/project_list.ts");
/******/ })
/************************************************************************/
/******/ ({

/***/ "./node_modules/natural-sort/dist/natural-sort.js":
/*!********************************************************!*\
  !*** ./node_modules/natural-sort/dist/natural-sort.js ***!
  \********************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

/*!
 * natural-sort.js
 * ===============
 * Sorting with support for numbers, dates, unicode and more.
 *
 * http://github.com/studio-b12/natural-sort
 * MIT License, © Studio B12 GmbH 2014
 *
 *//*
 *
 * Idea by Dave Koelle
 * Original implementation by Jim Palmer
 * Modified by Tomek Wiszniewski
 *
 */

var naturalSort = function naturalSort (options) { 'use strict';
  if (!options) options = {};

  return function(a, b) {
    var EQUAL = 0;
    var GREATER = (options.direction == 'desc' ?
      -1 :
      1
    );
    var SMALLER = -GREATER;

    var re = /(^-?[0-9]+(\.?[0-9]*)[df]?e?[0-9]?$|^0x[0-9a-f]+$|[0-9]+)/gi;
    var sre = /(^[ ]*|[ ]*$)/g;
    var dre = /(^([\w ]+,?[\w ]+)?[\w ]+,?[\w ]+\d+:\d+(:\d+)?[\w ]?|^\d{1,4}[\/\-]\d{1,4}[\/\-]\d{1,4}|^\w+, \w+ \d+, \d{4})/;
    var hre = /^0x[0-9a-f]+$/i;
    var ore = /^0/;

    var normalize = function normalize (value) {
      var string = '' + value;
      return (options.caseSensitive ?
        string :
        string.toLowerCase()
      );
    };

    // Normalize values to strings
    var x = normalize(a).replace(sre, '') || '';
    var y = normalize(b).replace(sre, '') || '';

    // chunk/tokenize
    var xN = x.replace(re, '\0$1\0').replace(/\0$/,'').replace(/^\0/,'').split('\0');
    var yN = y.replace(re, '\0$1\0').replace(/\0$/,'').replace(/^\0/,'').split('\0');

    // Return immediately if at least one of the values is empty.
    if (!x && !y) return EQUAL;
    if (!x &&  y) return GREATER;
    if ( x && !y) return SMALLER;

    // numeric, hex or date detection
    var xD = parseInt(x.match(hre)) || (xN.length != 1 && x.match(dre) && Date.parse(x));
    var yD = parseInt(y.match(hre)) || xD && y.match(dre) && Date.parse(y) || null;
    var oFxNcL, oFyNcL;

    // first try and sort Hex codes or Dates
    if (yD) {
      if ( xD < yD ) return SMALLER;
      else if ( xD > yD ) return GREATER;
    }

    // natural sorting through split numeric strings and default strings
    for (var cLoc=0, numS=Math.max(xN.length, yN.length); cLoc < numS; cLoc++) {

      // find floats not starting with '0', string or 0 if not defined (Clint Priest)
      oFxNcL = !(xN[cLoc] || '').match(ore) && parseFloat(xN[cLoc]) || xN[cLoc] || 0;
      oFyNcL = !(yN[cLoc] || '').match(ore) && parseFloat(yN[cLoc]) || yN[cLoc] || 0;

      // handle numeric vs string comparison - number < string - (Kyle Adams)
      if (isNaN(oFxNcL) !== isNaN(oFyNcL)) return (isNaN(oFxNcL)) ? GREATER : SMALLER;

      // rely on string comparison if different types - i.e. '02' < 2 != '02' < '2'
      else if (typeof oFxNcL !== typeof oFyNcL) {
        oFxNcL += '';
        oFyNcL += '';
      }

      if (oFxNcL < oFyNcL) return SMALLER;
      if (oFxNcL > oFyNcL) return GREATER;
    }

    return EQUAL;
  };
};

(function (root, factory) {
  if (true) {
    module.exports = factory();
  } else {}
}(this, function () {

  return naturalSort;

}));


/***/ }),

/***/ "./src/lib/multimap.ts":
/*!*****************************!*\
  !*** ./src/lib/multimap.ts ***!
  \*****************************/
/*! exports provided: ArrayListMultimap */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "ArrayListMultimap", function() { return ArrayListMultimap; });
/**
 * @author Jordan Luyke <jordanluyke@gmail.com>
 */
class ArrayListMultimap {
    constructor() {
        this._entries = [];
    }
    clear() {
        this._entries = [];
    }
    containsKey(key) {
        return this._entries.filter(entry => entry.key == key).length > 0;
    }
    containsValue(value) {
        return this._entries.filter(entry => entry.value == value).length > 0;
    }
    containsEntry(key, value) {
        return (this._entries.filter(entry => entry.key == key && entry.value == value).length > 0);
    }
    delete(key, value) {
        const temp = this._entries;
        this._entries = this._entries.filter(entry => {
            if (value)
                return entry.key != key || entry.value != value;
            return entry.key != key;
        });
        return temp.length != this._entries.length;
    }
    get entries() {
        return this._entries;
    }
    get(key) {
        return this._entries
            .filter(entry => entry.key == key)
            .map(entry => entry.value);
    }
    keys() {
        return Array.from(new Set(this._entries.map(entry => entry.key)));
    }
    put(key, value) {
        this._entries.push(new MultimapEntry(key, value));
        return this._entries;
    }
}
class MultimapEntry {
    constructor(key, value) {
        this.key = key;
        this.value = value;
    }
}


/***/ }),

/***/ "./src/project_list.ts":
/*!*****************************!*\
  !*** ./src/project_list.ts ***!
  \*****************************/
/*! no exports provided */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _systori_lib_multimap__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @systori/lib/multimap */ "./src/lib/multimap.ts");
/* harmony import */ var natural_sort__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! natural-sort */ "./node_modules/natural-sort/dist/natural-sort.js");
/* harmony import */ var natural_sort__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(natural_sort__WEBPACK_IMPORTED_MODULE_1__);


const searchRequestFired = false;
const attemptMade = false;
let searchMatches;
let phaseFilter;
const phaseOrder = [
    "prospective",
    "tendering",
    "planning",
    "executing",
    "settlement",
    "warranty",
    "finished",
];
function sortProjects(e) {
    if (e == null)
        return;
    let lookup = new Map();
    const i = 0;
    const btn = e.target;
    btn.activateExclusive();
    if (btn.type == "id") {
        Array.from(document.querySelectorAll(".tile")).map(e => lookup.set(parseInt(e.dataset["pk"] || "0"), e));
    }
    else if (btn.type == "name") {
        Array.from(document.querySelectorAll(".tile")).map(e => lookup.set(e.dataset["name"] || "", e));
    }
    else if (btn.type == "phase") {
        const lookup2 = new _systori_lib_multimap__WEBPACK_IMPORTED_MODULE_0__["ArrayListMultimap"]();
        lookup = new Map();
        Array.from(document.querySelectorAll(".tile")).map(e => lookup2.put(e.dataset["phase"] || "", e));
        for (const key of phaseOrder) {
            // for (let element of lookup2[key]) {
            //     console.log(element);
            // }
            console.log(key);
        }
    }
    let sortedKeys = Array.from(lookup.keys()).sort(natural_sort__WEBPACK_IMPORTED_MODULE_1___default()());
    if (btn.reversed == true) {
        sortedKeys = sortedKeys.reverse();
        btn.reversed = false;
    }
    else if (btn.reversed == false) {
        btn.reversed = true;
    }
    const lastMoved = null;
    for (const key of sortedKeys) {
        if (lastMoved == null) {
            console.log(`lastMoved == ${lastMoved} with key == ${key}`);
            // lastMoved = lookup[key];
            continue;
        }
        //lastMoved.insertAdjacentElement("afterend", lookup[key]);
        //last_moved = lookup[key];
    }
}
function filterProjects() {
    const warning = document.querySelector("sys-warning-message");
    warning.hideWarningMessage = true;
    const projects = document.querySelectorAll(".tile");
    for (const project of projects) {
        project.classList.add("hidden");
    }
}
function updatePhaseFilter(e) {
    if (e == undefined)
        return;
    const btn = e.target;
    btn.updatePhaseFilter();
    localStorage["phaseFilter"] = JSON.stringify({ phaseFilter });
    filterProjects();
}
class SystoriPhaseButton extends HTMLElement {
    constructor() {
        super(...arguments);
        this.tag = "sys-phase-button";
    }
    get phase() {
        return this.dataset["phase"] || "";
    }
    set phase(phase) {
        this.dataset["phase"] = phase;
    }
    get hidePhase() {
        return this.dataset["hide-phase"] == "true";
    }
    set hidePhase(hidePhase) {
        hidePhase
            ? (this.dataset["hide-phase"] = "true")
            : (this.dataset["hide-phase"] = "false");
    }
    get visiblePhase() {
        return !this.hidePhase;
    }
    hide() {
        this.hidePhase = true;
        phaseFilter = phaseFilter.filter(item => item != this.phase);
        this.classList.add("line_through");
    }
    show() {
        this.hidePhase = false;
        phaseFilter.push(this.phase);
        this.classList.remove("line_through");
    }
    updatePhaseFilter() {
        phaseFilter.includes(this.phase) ? this.hide() : this.show();
    }
    connectedCallback() {
        if (this.dataset["phase"])
            this.phase = this.dataset["phase"];
    }
}
class SystoriSortButton extends HTMLElement {
    constructor() {
        super(...arguments);
        this.tag = "sys-sort-button";
    }
    get type() {
        return this.dataset["type"] || "";
    }
    set type(type) {
        this.dataset["type"] = type;
    }
    get reversed() {
        return this.dataset["reversed"] == "true";
    }
    set reversed(reversed) {
        reversed
            ? (this.dataset["reversed"] = "true")
            : (this.dataset["reversed"] = "false");
    }
    get active() {
        return this.classList.contains("active");
    }
    set active(active) {
        active ? this.classList.add("active") : this.classList.remove("active");
    }
    activateExclusive() {
        const btns = Array.from(this.parentElement.querySelectorAll("sys-sort-button"));
        for (const btn of btns) {
            btn.active = false;
        }
        this.active = true;
        localStorage["sys-sort-button"] = this.type;
        localStorage["sys-sort-button-reversed"] = this.reversed.toString();
    }
    connectedCallback() {
        if (this.dataset["type"] != null)
            this.type = this.dataset["type"];
        if (this.dataset["reversed"] != null)
            this.reversed = this.dataset["reversed"] == "true";
    }
}
class SystoriProjectTile extends HTMLElement {
    constructor() {
        super(...arguments);
        this.tag = "sys-project-tile";
    }
    get hideProjectTile() {
        return this.classList.contains("hidden");
    }
    set hideProjectTile(hideProjectTile) {
        hideProjectTile
            ? this.classList.add("hidden")
            : this.classList.remove("hidden");
    }
}
class SystoriWarningMessage extends HTMLElement {
    constructor() {
        super(...arguments);
        this.tag = "sys-warning-message";
    }
    warnPhaseFilteredProjects(phaseFilteredProjects) {
        if (phaseFilteredProjects > 0) {
            this.children[0].innerHTML = document.querySelector("#sys-phaseFilteredProjects-translated").innerText;
            this.classList.remove("hidden");
        }
    }
    get hideWarningMessage() {
        return this.classList.contains("hidden");
    }
    set hideWarningMessage(hideWarningMessage) {
        hideWarningMessage
            ? this.classList.add("hidden")
            : this.classList.remove("hidden");
    }
}
function loadLocalStorage() {
    document.querySelector("#filter-bar").classList.remove("hidden");
    document.querySelector("#tile-container").classList.remove("hidden");
}
window.customElements.define("sys-phase-button", SystoriPhaseButton);
window.customElements.define("sys-sort-button", SystoriSortButton);
window.customElements.define("sys-project-tile", SystoriProjectTile);
window.customElements.define("sys-warning-message", SystoriWarningMessage);
// add Event Listeners
for (const btn of document.querySelectorAll("sys-sort-button")) {
    btn.addEventListener("click", sortProjects);
}
for (const btn of document.querySelectorAll("sys-phase-button")) {
    btn.addEventListener("click", updatePhaseFilter);
}
// Load user (browser) data
loadLocalStorage();


/***/ })

/******/ });
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8vd2VicGFjay9ib290c3RyYXAiLCJ3ZWJwYWNrOi8vLy4vbm9kZV9tb2R1bGVzL25hdHVyYWwtc29ydC9kaXN0L25hdHVyYWwtc29ydC5qcyIsIndlYnBhY2s6Ly8vLi9zcmMvbGliL211bHRpbWFwLnRzIiwid2VicGFjazovLy8uL3NyYy9wcm9qZWN0X2xpc3QudHMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IjtRQUFBO1FBQ0E7O1FBRUE7UUFDQTs7UUFFQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTs7UUFFQTtRQUNBOztRQUVBO1FBQ0E7O1FBRUE7UUFDQTtRQUNBOzs7UUFHQTtRQUNBOztRQUVBO1FBQ0E7O1FBRUE7UUFDQTtRQUNBO1FBQ0EsMENBQTBDLGdDQUFnQztRQUMxRTtRQUNBOztRQUVBO1FBQ0E7UUFDQTtRQUNBLHdEQUF3RCxrQkFBa0I7UUFDMUU7UUFDQSxpREFBaUQsY0FBYztRQUMvRDs7UUFFQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0EseUNBQXlDLGlDQUFpQztRQUMxRSxnSEFBZ0gsbUJBQW1CLEVBQUU7UUFDckk7UUFDQTs7UUFFQTtRQUNBO1FBQ0E7UUFDQSwyQkFBMkIsMEJBQTBCLEVBQUU7UUFDdkQsaUNBQWlDLGVBQWU7UUFDaEQ7UUFDQTtRQUNBOztRQUVBO1FBQ0Esc0RBQXNELCtEQUErRDs7UUFFckg7UUFDQTs7O1FBR0E7UUFDQTs7Ozs7Ozs7Ozs7O0FDbEZBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUFFQSxrREFBa0Q7QUFDbEQ7O0FBRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FBRUE7QUFDQTtBQUNBLHlFQUF5RSxJQUFJLFNBQVMsSUFBSSxTQUFTLElBQUksbUJBQW1CLEVBQUU7QUFDNUg7QUFD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O0FBQ3JFLE1BQU0sQ0FBQyxjQUFjLENBQUMsTUFBTSxDQUFDLGlCQUFpQixFQUFFLGlCQUFpQixDQUFDLENBQUM7QUFDbkUsTUFBTSxDQUFDLGNBQWMsQ0FBQyxNQUFNLENBQUMsa0JBQWtCLEVBQUUsa0JBQWtCLENBQUMsQ0FBQztBQUNyRSxNQUFNLENBQUMsY0FBYyxDQUFDLE1BQU0sQ0FBQyxxQkFBcUIsRUFBRSxxQkFBcUIsQ0FBQyxDQUFDO0FBRTNFLHNCQUFzQjtBQUN0QixLQUFLLE1BQU0sR0FBRyxJQUFJLFFBQVEsQ0FBQyxnQkFBZ0IsQ0FDdkMsaUJBQWlCLENBQ3BCLEVBQUU7SUFDQyxHQUFHLENBQUMsZ0JBQWdCLENBQUMsT0FBTyxFQUFFLFlBQVksQ0FBQyxDQUFDO0NBQy9DO0FBRUQsS0FBSyxNQUFNLEdBQUcsSUFBSSxRQUFRLENBQUMsZ0JBQWdCLENBQ3ZDLGtCQUFrQixDQUNyQixFQUFFO0lBQ0MsR0FBRyxDQUFDLGdCQUFnQixDQUFDLE9BQU8sRUFBRSxpQkFBaUIsQ0FBQyxDQUFDO0NBQ3BEO0FBRUQsMkJBQTJCO0FBQzNCLGdCQUFnQixFQUFFLENBQUMiLCJmaWxlIjoicHJvamVjdF9saXN0LmpzIiwic291cmNlc0NvbnRlbnQiOlsiIFx0Ly8gVGhlIG1vZHVsZSBjYWNoZVxuIFx0dmFyIGluc3RhbGxlZE1vZHVsZXMgPSB7fTtcblxuIFx0Ly8gVGhlIHJlcXVpcmUgZnVuY3Rpb25cbiBcdGZ1bmN0aW9uIF9fd2VicGFja19yZXF1aXJlX18obW9kdWxlSWQpIHtcblxuIFx0XHQvLyBDaGVjayBpZiBtb2R1bGUgaXMgaW4gY2FjaGVcbiBcdFx0aWYoaW5zdGFsbGVkTW9kdWxlc1ttb2R1bGVJZF0pIHtcbiBcdFx0XHRyZXR1cm4gaW5zdGFsbGVkTW9kdWxlc1ttb2R1bGVJZF0uZXhwb3J0cztcbiBcdFx0fVxuIFx0XHQvLyBDcmVhdGUgYSBuZXcgbW9kdWxlIChhbmQgcHV0IGl0IGludG8gdGhlIGNhY2hlKVxuIFx0XHR2YXIgbW9kdWxlID0gaW5zdGFsbGVkTW9kdWxlc1ttb2R1bGVJZF0gPSB7XG4gXHRcdFx0aTogbW9kdWxlSWQsXG4gXHRcdFx0bDogZmFsc2UsXG4gXHRcdFx0ZXhwb3J0czoge31cbiBcdFx0fTtcblxuIFx0XHQvLyBFeGVjdXRlIHRoZSBtb2R1bGUgZnVuY3Rpb25cbiBcdFx0bW9kdWxlc1ttb2R1bGVJZF0uY2FsbChtb2R1bGUuZXhwb3J0cywgbW9kdWxlLCBtb2R1bGUuZXhwb3J0cywgX193ZWJwYWNrX3JlcXVpcmVfXyk7XG5cbiBcdFx0Ly8gRmxhZyB0aGUgbW9kdWxlIGFzIGxvYWRlZFxuIFx0XHRtb2R1bGUubCA9IHRydWU7XG5cbiBcdFx0Ly8gUmV0dXJuIHRoZSBleHBvcnRzIG9mIHRoZSBtb2R1bGVcbiBcdFx0cmV0dXJuIG1vZHVsZS5leHBvcnRzO1xuIFx0fVxuXG5cbiBcdC8vIGV4cG9zZSB0aGUgbW9kdWxlcyBvYmplY3QgKF9fd2VicGFja19tb2R1bGVzX18pXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLm0gPSBtb2R1bGVzO1xuXG4gXHQvLyBleHBvc2UgdGhlIG1vZHVsZSBjYWNoZVxuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy5jID0gaW5zdGFsbGVkTW9kdWxlcztcblxuIFx0Ly8gZGVmaW5lIGdldHRlciBmdW5jdGlvbiBmb3IgaGFybW9ueSBleHBvcnRzXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLmQgPSBmdW5jdGlvbihleHBvcnRzLCBuYW1lLCBnZXR0ZXIpIHtcbiBcdFx0aWYoIV9fd2VicGFja19yZXF1aXJlX18ubyhleHBvcnRzLCBuYW1lKSkge1xuIFx0XHRcdE9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBuYW1lLCB7IGVudW1lcmFibGU6IHRydWUsIGdldDogZ2V0dGVyIH0pO1xuIFx0XHR9XG4gXHR9O1xuXG4gXHQvLyBkZWZpbmUgX19lc01vZHVsZSBvbiBleHBvcnRzXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLnIgPSBmdW5jdGlvbihleHBvcnRzKSB7XG4gXHRcdGlmKHR5cGVvZiBTeW1ib2wgIT09ICd1bmRlZmluZWQnICYmIFN5bWJvbC50b1N0cmluZ1RhZykge1xuIFx0XHRcdE9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBTeW1ib2wudG9TdHJpbmdUYWcsIHsgdmFsdWU6ICdNb2R1bGUnIH0pO1xuIFx0XHR9XG4gXHRcdE9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCAnX19lc01vZHVsZScsIHsgdmFsdWU6IHRydWUgfSk7XG4gXHR9O1xuXG4gXHQvLyBjcmVhdGUgYSBmYWtlIG5hbWVzcGFjZSBvYmplY3RcbiBcdC8vIG1vZGUgJiAxOiB2YWx1ZSBpcyBhIG1vZHVsZSBpZCwgcmVxdWlyZSBpdFxuIFx0Ly8gbW9kZSAmIDI6IG1lcmdlIGFsbCBwcm9wZXJ0aWVzIG9mIHZhbHVlIGludG8gdGhlIG5zXG4gXHQvLyBtb2RlICYgNDogcmV0dXJuIHZhbHVlIHdoZW4gYWxyZWFkeSBucyBvYmplY3RcbiBcdC8vIG1vZGUgJiA4fDE6IGJlaGF2ZSBsaWtlIHJlcXVpcmVcbiBcdF9fd2VicGFja19yZXF1aXJlX18udCA9IGZ1bmN0aW9uKHZhbHVlLCBtb2RlKSB7XG4gXHRcdGlmKG1vZGUgJiAxKSB2YWx1ZSA9IF9fd2VicGFja19yZXF1aXJlX18odmFsdWUpO1xuIFx0XHRpZihtb2RlICYgOCkgcmV0dXJuIHZhbHVlO1xuIFx0XHRpZigobW9kZSAmIDQpICYmIHR5cGVvZiB2YWx1ZSA9PT0gJ29iamVjdCcgJiYgdmFsdWUgJiYgdmFsdWUuX19lc01vZHVsZSkgcmV0dXJuIHZhbHVlO1xuIFx0XHR2YXIgbnMgPSBPYmplY3QuY3JlYXRlKG51bGwpO1xuIFx0XHRfX3dlYnBhY2tfcmVxdWlyZV9fLnIobnMpO1xuIFx0XHRPYmplY3QuZGVmaW5lUHJvcGVydHkobnMsICdkZWZhdWx0JywgeyBlbnVtZXJhYmxlOiB0cnVlLCB2YWx1ZTogdmFsdWUgfSk7XG4gXHRcdGlmKG1vZGUgJiAyICYmIHR5cGVvZiB2YWx1ZSAhPSAnc3RyaW5nJykgZm9yKHZhciBrZXkgaW4gdmFsdWUpIF9fd2VicGFja19yZXF1aXJlX18uZChucywga2V5LCBmdW5jdGlvbihrZXkpIHsgcmV0dXJuIHZhbHVlW2tleV07IH0uYmluZChudWxsLCBrZXkpKTtcbiBcdFx0cmV0dXJuIG5zO1xuIFx0fTtcblxuIFx0Ly8gZ2V0RGVmYXVsdEV4cG9ydCBmdW5jdGlvbiBmb3IgY29tcGF0aWJpbGl0eSB3aXRoIG5vbi1oYXJtb255IG1vZHVsZXNcbiBcdF9fd2VicGFja19yZXF1aXJlX18ubiA9IGZ1bmN0aW9uKG1vZHVsZSkge1xuIFx0XHR2YXIgZ2V0dGVyID0gbW9kdWxlICYmIG1vZHVsZS5fX2VzTW9kdWxlID9cbiBcdFx0XHRmdW5jdGlvbiBnZXREZWZhdWx0KCkgeyByZXR1cm4gbW9kdWxlWydkZWZhdWx0J107IH0gOlxuIFx0XHRcdGZ1bmN0aW9uIGdldE1vZHVsZUV4cG9ydHMoKSB7IHJldHVybiBtb2R1bGU7IH07XG4gXHRcdF9fd2VicGFja19yZXF1aXJlX18uZChnZXR0ZXIsICdhJywgZ2V0dGVyKTtcbiBcdFx0cmV0dXJuIGdldHRlcjtcbiBcdH07XG5cbiBcdC8vIE9iamVjdC5wcm90b3R5cGUuaGFzT3duUHJvcGVydHkuY2FsbFxuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy5vID0gZnVuY3Rpb24ob2JqZWN0LCBwcm9wZXJ0eSkgeyByZXR1cm4gT2JqZWN0LnByb3RvdHlwZS5oYXNPd25Qcm9wZXJ0eS5jYWxsKG9iamVjdCwgcHJvcGVydHkpOyB9O1xuXG4gXHQvLyBfX3dlYnBhY2tfcHVibGljX3BhdGhfX1xuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy5wID0gXCJcIjtcblxuXG4gXHQvLyBMb2FkIGVudHJ5IG1vZHVsZSBhbmQgcmV0dXJuIGV4cG9ydHNcbiBcdHJldHVybiBfX3dlYnBhY2tfcmVxdWlyZV9fKF9fd2VicGFja19yZXF1aXJlX18ucyA9IFwiLi9zcmMvcHJvamVjdF9saXN0LnRzXCIpO1xuIiwiLyohXG4gKiBuYXR1cmFsLXNvcnQuanNcbiAqID09PT09PT09PT09PT09PVxuICogU29ydGluZyB3aXRoIHN1cHBvcnQgZm9yIG51bWJlcnMsIGRhdGVzLCB1bmljb2RlIGFuZCBtb3JlLlxuICpcbiAqIGh0dHA6Ly9naXRodWIuY29tL3N0dWRpby1iMTIvbmF0dXJhbC1zb3J0XG4gKiBNSVQgTGljZW5zZSwgwqkgU3R1ZGlvIEIxMiBHbWJIIDIwMTRcbiAqXG4gKi8vKlxuICpcbiAqIElkZWEgYnkgRGF2ZSBLb2VsbGVcbiAqIE9yaWdpbmFsIGltcGxlbWVudGF0aW9uIGJ5IEppbSBQYWxtZXJcbiAqIE1vZGlmaWVkIGJ5IFRvbWVrIFdpc3puaWV3c2tpXG4gKlxuICovXG5cbnZhciBuYXR1cmFsU29ydCA9IGZ1bmN0aW9uIG5hdHVyYWxTb3J0IChvcHRpb25zKSB7ICd1c2Ugc3RyaWN0JztcbiAgaWYgKCFvcHRpb25zKSBvcHRpb25zID0ge307XG5cbiAgcmV0dXJuIGZ1bmN0aW9uKGEsIGIpIHtcbiAgICB2YXIgRVFVQUwgPSAwO1xuICAgIHZhciBHUkVBVEVSID0gKG9wdGlvbnMuZGlyZWN0aW9uID09ICdkZXNjJyA/XG4gICAgICAtMSA6XG4gICAgICAxXG4gICAgKTtcbiAgICB2YXIgU01BTExFUiA9IC1HUkVBVEVSO1xuXG4gICAgdmFyIHJlID0gLyheLT9bMC05XSsoXFwuP1swLTldKilbZGZdP2U/WzAtOV0/JHxeMHhbMC05YS1mXSskfFswLTldKykvZ2k7XG4gICAgdmFyIHNyZSA9IC8oXlsgXSp8WyBdKiQpL2c7XG4gICAgdmFyIGRyZSA9IC8oXihbXFx3IF0rLD9bXFx3IF0rKT9bXFx3IF0rLD9bXFx3IF0rXFxkKzpcXGQrKDpcXGQrKT9bXFx3IF0/fF5cXGR7MSw0fVtcXC9cXC1dXFxkezEsNH1bXFwvXFwtXVxcZHsxLDR9fF5cXHcrLCBcXHcrIFxcZCssIFxcZHs0fSkvO1xuICAgIHZhciBocmUgPSAvXjB4WzAtOWEtZl0rJC9pO1xuICAgIHZhciBvcmUgPSAvXjAvO1xuXG4gICAgdmFyIG5vcm1hbGl6ZSA9IGZ1bmN0aW9uIG5vcm1hbGl6ZSAodmFsdWUpIHtcbiAgICAgIHZhciBzdHJpbmcgPSAnJyArIHZhbHVlO1xuICAgICAgcmV0dXJuIChvcHRpb25zLmNhc2VTZW5zaXRpdmUgP1xuICAgICAgICBzdHJpbmcgOlxuICAgICAgICBzdHJpbmcudG9Mb3dlckNhc2UoKVxuICAgICAgKTtcbiAgICB9O1xuXG4gICAgLy8gTm9ybWFsaXplIHZhbHVlcyB0byBzdHJpbmdzXG4gICAgdmFyIHggPSBub3JtYWxpemUoYSkucmVwbGFjZShzcmUsICcnKSB8fCAnJztcbiAgICB2YXIgeSA9IG5vcm1hbGl6ZShiKS5yZXBsYWNlKHNyZSwgJycpIHx8ICcnO1xuXG4gICAgLy8gY2h1bmsvdG9rZW5pemVcbiAgICB2YXIgeE4gPSB4LnJlcGxhY2UocmUsICdcXDAkMVxcMCcpLnJlcGxhY2UoL1xcMCQvLCcnKS5yZXBsYWNlKC9eXFwwLywnJykuc3BsaXQoJ1xcMCcpO1xuICAgIHZhciB5TiA9IHkucmVwbGFjZShyZSwgJ1xcMCQxXFwwJykucmVwbGFjZSgvXFwwJC8sJycpLnJlcGxhY2UoL15cXDAvLCcnKS5zcGxpdCgnXFwwJyk7XG5cbiAgICAvLyBSZXR1cm4gaW1tZWRpYXRlbHkgaWYgYXQgbGVhc3Qgb25lIG9mIHRoZSB2YWx1ZXMgaXMgZW1wdHkuXG4gICAgaWYgKCF4ICYmICF5KSByZXR1cm4gRVFVQUw7XG4gICAgaWYgKCF4ICYmICB5KSByZXR1cm4gR1JFQVRFUjtcbiAgICBpZiAoIHggJiYgIXkpIHJldHVybiBTTUFMTEVSO1xuXG4gICAgLy8gbnVtZXJpYywgaGV4IG9yIGRhdGUgZGV0ZWN0aW9uXG4gICAgdmFyIHhEID0gcGFyc2VJbnQoeC5tYXRjaChocmUpKSB8fCAoeE4ubGVuZ3RoICE9IDEgJiYgeC5tYXRjaChkcmUpICYmIERhdGUucGFyc2UoeCkpO1xuICAgIHZhciB5RCA9IHBhcnNlSW50KHkubWF0Y2goaHJlKSkgfHwgeEQgJiYgeS5tYXRjaChkcmUpICYmIERhdGUucGFyc2UoeSkgfHwgbnVsbDtcbiAgICB2YXIgb0Z4TmNMLCBvRnlOY0w7XG5cbiAgICAvLyBmaXJzdCB0cnkgYW5kIHNvcnQgSGV4IGNvZGVzIG9yIERhdGVzXG4gICAgaWYgKHlEKSB7XG4gICAgICBpZiAoIHhEIDwgeUQgKSByZXR1cm4gU01BTExFUjtcbiAgICAgIGVsc2UgaWYgKCB4RCA+IHlEICkgcmV0dXJuIEdSRUFURVI7XG4gICAgfVxuXG4gICAgLy8gbmF0dXJhbCBzb3J0aW5nIHRocm91Z2ggc3BsaXQgbnVtZXJpYyBzdHJpbmdzIGFuZCBkZWZhdWx0IHN0cmluZ3NcbiAgICBmb3IgKHZhciBjTG9jPTAsIG51bVM9TWF0aC5tYXgoeE4ubGVuZ3RoLCB5Ti5sZW5ndGgpOyBjTG9jIDwgbnVtUzsgY0xvYysrKSB7XG5cbiAgICAgIC8vIGZpbmQgZmxvYXRzIG5vdCBzdGFydGluZyB3aXRoICcwJywgc3RyaW5nIG9yIDAgaWYgbm90IGRlZmluZWQgKENsaW50IFByaWVzdClcbiAgICAgIG9GeE5jTCA9ICEoeE5bY0xvY10gfHwgJycpLm1hdGNoKG9yZSkgJiYgcGFyc2VGbG9hdCh4TltjTG9jXSkgfHwgeE5bY0xvY10gfHwgMDtcbiAgICAgIG9GeU5jTCA9ICEoeU5bY0xvY10gfHwgJycpLm1hdGNoKG9yZSkgJiYgcGFyc2VGbG9hdCh5TltjTG9jXSkgfHwgeU5bY0xvY10gfHwgMDtcblxuICAgICAgLy8gaGFuZGxlIG51bWVyaWMgdnMgc3RyaW5nIGNvbXBhcmlzb24gLSBudW1iZXIgPCBzdHJpbmcgLSAoS3lsZSBBZGFtcylcbiAgICAgIGlmIChpc05hTihvRnhOY0wpICE9PSBpc05hTihvRnlOY0wpKSByZXR1cm4gKGlzTmFOKG9GeE5jTCkpID8gR1JFQVRFUiA6IFNNQUxMRVI7XG5cbiAgICAgIC8vIHJlbHkgb24gc3RyaW5nIGNvbXBhcmlzb24gaWYgZGlmZmVyZW50IHR5cGVzIC0gaS5lLiAnMDInIDwgMiAhPSAnMDInIDwgJzInXG4gICAgICBlbHNlIGlmICh0eXBlb2Ygb0Z4TmNMICE9PSB0eXBlb2Ygb0Z5TmNMKSB7XG4gICAgICAgIG9GeE5jTCArPSAnJztcbiAgICAgICAgb0Z5TmNMICs9ICcnO1xuICAgICAgfVxuXG4gICAgICBpZiAob0Z4TmNMIDwgb0Z5TmNMKSByZXR1cm4gU01BTExFUjtcbiAgICAgIGlmIChvRnhOY0wgPiBvRnlOY0wpIHJldHVybiBHUkVBVEVSO1xuICAgIH1cblxuICAgIHJldHVybiBFUVVBTDtcbiAgfTtcbn07XG5cbihmdW5jdGlvbiAocm9vdCwgZmFjdG9yeSkge1xuICBpZiAodHlwZW9mIGV4cG9ydHMgPT09ICdvYmplY3QnKSB7XG4gICAgbW9kdWxlLmV4cG9ydHMgPSBmYWN0b3J5KCk7XG4gIH0gZWxzZSB7XG4gICAgcm9vdC5uYXR1cmFsU29ydCA9IGZhY3RvcnkoKTtcbiAgfVxufSh0aGlzLCBmdW5jdGlvbiAoKSB7XG5cbiAgcmV0dXJuIG5hdHVyYWxTb3J0O1xuXG59KSk7XG4iLCIvKipcbiAqIEBhdXRob3IgSm9yZGFuIEx1eWtlIDxqb3JkYW5sdXlrZUBnbWFpbC5jb20+XG4gKi9cblxuZXhwb3J0IGludGVyZmFjZSBNdWx0aW1hcDxLLCBWPiB7XG4gICAgY2xlYXIoKTogdm9pZDtcbiAgICBjb250YWluc0tleShrZXk6IEspOiBib29sZWFuO1xuICAgIGNvbnRhaW5zVmFsdWUodmFsdWU6IFYpOiBib29sZWFuO1xuICAgIGNvbnRhaW5zRW50cnkoa2V5OiBLLCB2YWx1ZTogVik6IGJvb2xlYW47XG4gICAgZGVsZXRlKGtleTogSywgdmFsdWU/OiBWKTogYm9vbGVhbjtcbiAgICBlbnRyaWVzOiBNdWx0aW1hcEVudHJ5PEssIFY+W107XG4gICAgZ2V0KGtleTogSyk6IFZbXTtcbiAgICBrZXlzKCk6IEtbXTtcbiAgICBwdXQoa2V5OiBLLCB2YWx1ZTogVik6IE11bHRpbWFwRW50cnk8SywgVj5bXTtcbn1cblxuZXhwb3J0IGNsYXNzIEFycmF5TGlzdE11bHRpbWFwPEssIFY+IGltcGxlbWVudHMgTXVsdGltYXA8SywgVj4ge1xuICAgIHByaXZhdGUgX2VudHJpZXM6IE11bHRpbWFwRW50cnk8SywgVj5bXSA9IFtdO1xuXG4gICAgcHVibGljIGNsZWFyKCk6IHZvaWQge1xuICAgICAgICB0aGlzLl9lbnRyaWVzID0gW107XG4gICAgfVxuXG4gICAgcHVibGljIGNvbnRhaW5zS2V5KGtleTogSyk6IGJvb2xlYW4ge1xuICAgICAgICByZXR1cm4gdGhpcy5fZW50cmllcy5maWx0ZXIoZW50cnkgPT4gZW50cnkua2V5ID09IGtleSkubGVuZ3RoID4gMDtcbiAgICB9XG5cbiAgICBwdWJsaWMgY29udGFpbnNWYWx1ZSh2YWx1ZTogVik6IGJvb2xlYW4ge1xuICAgICAgICByZXR1cm4gdGhpcy5fZW50cmllcy5maWx0ZXIoZW50cnkgPT4gZW50cnkudmFsdWUgPT0gdmFsdWUpLmxlbmd0aCA+IDA7XG4gICAgfVxuXG4gICAgcHVibGljIGNvbnRhaW5zRW50cnkoa2V5OiBLLCB2YWx1ZTogVik6IGJvb2xlYW4ge1xuICAgICAgICByZXR1cm4gKFxuICAgICAgICAgICAgdGhpcy5fZW50cmllcy5maWx0ZXIoXG4gICAgICAgICAgICAgICAgZW50cnkgPT4gZW50cnkua2V5ID09IGtleSAmJiBlbnRyeS52YWx1ZSA9PSB2YWx1ZSxcbiAgICAgICAgICAgICkubGVuZ3RoID4gMFxuICAgICAgICApO1xuICAgIH1cblxuICAgIHB1YmxpYyBkZWxldGUoa2V5OiBLLCB2YWx1ZT86IFYpOiBib29sZWFuIHtcbiAgICAgICAgY29uc3QgdGVtcCA9IHRoaXMuX2VudHJpZXM7XG4gICAgICAgIHRoaXMuX2VudHJpZXMgPSB0aGlzLl9lbnRyaWVzLmZpbHRlcihlbnRyeSA9PiB7XG4gICAgICAgICAgICBpZiAodmFsdWUpIHJldHVybiBlbnRyeS5rZXkgIT0ga2V5IHx8IGVudHJ5LnZhbHVlICE9IHZhbHVlO1xuICAgICAgICAgICAgcmV0dXJuIGVudHJ5LmtleSAhPSBrZXk7XG4gICAgICAgIH0pO1xuICAgICAgICByZXR1cm4gdGVtcC5sZW5ndGggIT0gdGhpcy5fZW50cmllcy5sZW5ndGg7XG4gICAgfVxuXG4gICAgcHVibGljIGdldCBlbnRyaWVzKCk6IE11bHRpbWFwRW50cnk8SywgVj5bXSB7XG4gICAgICAgIHJldHVybiB0aGlzLl9lbnRyaWVzO1xuICAgIH1cblxuICAgIHB1YmxpYyBnZXQoa2V5OiBLKTogVltdIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuX2VudHJpZXNcbiAgICAgICAgICAgIC5maWx0ZXIoZW50cnkgPT4gZW50cnkua2V5ID09IGtleSlcbiAgICAgICAgICAgIC5tYXAoZW50cnkgPT4gZW50cnkudmFsdWUpO1xuICAgIH1cblxuICAgIHB1YmxpYyBrZXlzKCk6IEtbXSB7XG4gICAgICAgIHJldHVybiBBcnJheS5mcm9tKG5ldyBTZXQodGhpcy5fZW50cmllcy5tYXAoZW50cnkgPT4gZW50cnkua2V5KSkpO1xuICAgIH1cblxuICAgIHB1YmxpYyBwdXQoa2V5OiBLLCB2YWx1ZTogVik6IE11bHRpbWFwRW50cnk8SywgVj5bXSB7XG4gICAgICAgIHRoaXMuX2VudHJpZXMucHVzaChuZXcgTXVsdGltYXBFbnRyeShrZXksIHZhbHVlKSk7XG4gICAgICAgIHJldHVybiB0aGlzLl9lbnRyaWVzO1xuICAgIH1cbn1cblxuY2xhc3MgTXVsdGltYXBFbnRyeTxLLCBWPiB7XG4gICAgY29uc3RydWN0b3IocmVhZG9ubHkga2V5OiBLLCByZWFkb25seSB2YWx1ZTogVikge31cbn1cbiIsImltcG9ydCB7IEFycmF5TGlzdE11bHRpbWFwLCBNdWx0aW1hcCB9IGZyb20gXCJAc3lzdG9yaS9saWIvbXVsdGltYXBcIjtcbmltcG9ydCBuYXR1cmFsU29ydCBmcm9tIFwibmF0dXJhbC1zb3J0XCI7XG5cbmNvbnN0IHNlYXJjaFJlcXVlc3RGaXJlZCA9IGZhbHNlO1xuY29uc3QgYXR0ZW1wdE1hZGUgPSBmYWxzZTtcbmxldCBzZWFyY2hNYXRjaGVzOiBBcnJheTxudW1iZXI+O1xubGV0IHBoYXNlRmlsdGVyOiBBcnJheTxzdHJpbmc+O1xuY29uc3QgcGhhc2VPcmRlcjogQXJyYXk8c3RyaW5nPiA9IFtcbiAgICBcInByb3NwZWN0aXZlXCIsXG4gICAgXCJ0ZW5kZXJpbmdcIixcbiAgICBcInBsYW5uaW5nXCIsXG4gICAgXCJleGVjdXRpbmdcIixcbiAgICBcInNldHRsZW1lbnRcIixcbiAgICBcIndhcnJhbnR5XCIsXG4gICAgXCJmaW5pc2hlZFwiLFxuXTtcblxuZnVuY3Rpb24gc29ydFByb2plY3RzKGU6IEV2ZW50KTogdm9pZCB7XG4gICAgaWYgKGUgPT0gbnVsbCkgcmV0dXJuO1xuICAgIGxldCBsb29rdXA6IE1hcDxhbnksIFN5c3RvcmlQcm9qZWN0VGlsZT4gPSBuZXcgTWFwKCk7XG4gICAgY29uc3QgaSA9IDA7XG5cbiAgICBjb25zdCBidG4gPSBlLnRhcmdldCBhcyBTeXN0b3JpU29ydEJ1dHRvbjtcbiAgICBidG4uYWN0aXZhdGVFeGNsdXNpdmUoKTtcblxuICAgIGlmIChidG4udHlwZSA9PSBcImlkXCIpIHtcbiAgICAgICAgQXJyYXkuZnJvbShkb2N1bWVudC5xdWVyeVNlbGVjdG9yQWxsPFN5c3RvcmlQcm9qZWN0VGlsZT4oXCIudGlsZVwiKSkubWFwKFxuICAgICAgICAgICAgZSA9PiBsb29rdXAuc2V0KHBhcnNlSW50KGUuZGF0YXNldFtcInBrXCJdIHx8IFwiMFwiKSwgZSksXG4gICAgICAgICk7XG4gICAgfSBlbHNlIGlmIChidG4udHlwZSA9PSBcIm5hbWVcIikge1xuICAgICAgICBBcnJheS5mcm9tKGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGw8U3lzdG9yaVByb2plY3RUaWxlPihcIi50aWxlXCIpKS5tYXAoXG4gICAgICAgICAgICBlID0+IGxvb2t1cC5zZXQoZS5kYXRhc2V0W1wibmFtZVwiXSB8fCBcIlwiLCBlKSxcbiAgICAgICAgKTtcbiAgICB9IGVsc2UgaWYgKGJ0bi50eXBlID09IFwicGhhc2VcIikge1xuICAgICAgICBjb25zdCBsb29rdXAyOiBNdWx0aW1hcDxzdHJpbmcsIEhUTUxFbGVtZW50PiA9IG5ldyBBcnJheUxpc3RNdWx0aW1hcCgpO1xuICAgICAgICBsb29rdXAgPSBuZXcgTWFwKCk7XG4gICAgICAgIEFycmF5LmZyb20oZG9jdW1lbnQucXVlcnlTZWxlY3RvckFsbDxTeXN0b3JpUHJvamVjdFRpbGU+KFwiLnRpbGVcIikpLm1hcChcbiAgICAgICAgICAgIGUgPT4gbG9va3VwMi5wdXQoZS5kYXRhc2V0W1wicGhhc2VcIl0gfHwgXCJcIiwgZSksXG4gICAgICAgICk7XG4gICAgICAgIGZvciAoY29uc3Qga2V5IG9mIHBoYXNlT3JkZXIpIHtcbiAgICAgICAgICAgIC8vIGZvciAobGV0IGVsZW1lbnQgb2YgbG9va3VwMltrZXldKSB7XG4gICAgICAgICAgICAvLyAgICAgY29uc29sZS5sb2coZWxlbWVudCk7XG4gICAgICAgICAgICAvLyB9XG4gICAgICAgICAgICBjb25zb2xlLmxvZyhrZXkpO1xuICAgICAgICB9XG4gICAgfVxuXG4gICAgbGV0IHNvcnRlZEtleXM6IEFycmF5PG51bWJlcj4gPSBBcnJheS5mcm9tKGxvb2t1cC5rZXlzKCkpLnNvcnQoXG4gICAgICAgIG5hdHVyYWxTb3J0KCksXG4gICAgKTtcbiAgICBpZiAoYnRuLnJldmVyc2VkID09IHRydWUpIHtcbiAgICAgICAgc29ydGVkS2V5cyA9IHNvcnRlZEtleXMucmV2ZXJzZSgpO1xuICAgICAgICBidG4ucmV2ZXJzZWQgPSBmYWxzZTtcbiAgICB9IGVsc2UgaWYgKGJ0bi5yZXZlcnNlZCA9PSBmYWxzZSkge1xuICAgICAgICBidG4ucmV2ZXJzZWQgPSB0cnVlO1xuICAgIH1cblxuICAgIGNvbnN0IGxhc3RNb3ZlZCA9IG51bGw7XG5cbiAgICBmb3IgKGNvbnN0IGtleSBvZiBzb3J0ZWRLZXlzKSB7XG4gICAgICAgIGlmIChsYXN0TW92ZWQgPT0gbnVsbCkge1xuICAgICAgICAgICAgY29uc29sZS5sb2coYGxhc3RNb3ZlZCA9PSAke2xhc3RNb3ZlZH0gd2l0aCBrZXkgPT0gJHtrZXl9YCk7XG4gICAgICAgICAgICAvLyBsYXN0TW92ZWQgPSBsb29rdXBba2V5XTtcbiAgICAgICAgICAgIGNvbnRpbnVlO1xuICAgICAgICB9XG4gICAgICAgIC8vbGFzdE1vdmVkLmluc2VydEFkamFjZW50RWxlbWVudChcImFmdGVyZW5kXCIsIGxvb2t1cFtrZXldKTtcbiAgICAgICAgLy9sYXN0X21vdmVkID0gbG9va3VwW2tleV07XG4gICAgfVxufVxuXG5mdW5jdGlvbiBmaWx0ZXJQcm9qZWN0cygpOiB2b2lkIHtcbiAgICBjb25zdCB3YXJuaW5nID0gZG9jdW1lbnQucXVlcnlTZWxlY3RvcihcbiAgICAgICAgXCJzeXMtd2FybmluZy1tZXNzYWdlXCIsXG4gICAgKSBhcyBTeXN0b3JpV2FybmluZ01lc3NhZ2U7XG4gICAgd2FybmluZy5oaWRlV2FybmluZ01lc3NhZ2UgPSB0cnVlO1xuXG4gICAgY29uc3QgcHJvamVjdHMgPSBkb2N1bWVudC5xdWVyeVNlbGVjdG9yQWxsPFN5c3RvcmlQcm9qZWN0VGlsZT4oXCIudGlsZVwiKTtcbiAgICBmb3IgKGNvbnN0IHByb2plY3Qgb2YgcHJvamVjdHMpIHtcbiAgICAgICAgcHJvamVjdC5jbGFzc0xpc3QuYWRkKFwiaGlkZGVuXCIpO1xuICAgIH1cbn1cblxuZnVuY3Rpb24gdXBkYXRlUGhhc2VGaWx0ZXIoZTogRXZlbnQpOiB2b2lkIHtcbiAgICBpZiAoZSA9PSB1bmRlZmluZWQpIHJldHVybjtcbiAgICBjb25zdCBidG4gPSBlLnRhcmdldCBhcyBTeXN0b3JpUGhhc2VCdXR0b247XG4gICAgYnRuLnVwZGF0ZVBoYXNlRmlsdGVyKCk7XG4gICAgbG9jYWxTdG9yYWdlW1wicGhhc2VGaWx0ZXJcIl0gPSBKU09OLnN0cmluZ2lmeSh7IHBoYXNlRmlsdGVyIH0pO1xuICAgIGZpbHRlclByb2plY3RzKCk7XG59XG5cbmNsYXNzIFN5c3RvcmlQaGFzZUJ1dHRvbiBleHRlbmRzIEhUTUxFbGVtZW50IHtcbiAgICB0YWcgPSBcInN5cy1waGFzZS1idXR0b25cIjtcblxuICAgIGdldCBwaGFzZSgpOiBzdHJpbmcge1xuICAgICAgICByZXR1cm4gdGhpcy5kYXRhc2V0W1wicGhhc2VcIl0gfHwgXCJcIjtcbiAgICB9XG4gICAgc2V0IHBoYXNlKHBoYXNlOiBzdHJpbmcpIHtcbiAgICAgICAgdGhpcy5kYXRhc2V0W1wicGhhc2VcIl0gPSBwaGFzZTtcbiAgICB9XG5cbiAgICBnZXQgaGlkZVBoYXNlKCk6IGJvb2xlYW4ge1xuICAgICAgICByZXR1cm4gdGhpcy5kYXRhc2V0W1wiaGlkZS1waGFzZVwiXSA9PSBcInRydWVcIjtcbiAgICB9XG4gICAgc2V0IGhpZGVQaGFzZShoaWRlUGhhc2U6IGJvb2xlYW4pIHtcbiAgICAgICAgaGlkZVBoYXNlXG4gICAgICAgICAgICA/ICh0aGlzLmRhdGFzZXRbXCJoaWRlLXBoYXNlXCJdID0gXCJ0cnVlXCIpXG4gICAgICAgICAgICA6ICh0aGlzLmRhdGFzZXRbXCJoaWRlLXBoYXNlXCJdID0gXCJmYWxzZVwiKTtcbiAgICB9XG4gICAgZ2V0IHZpc2libGVQaGFzZSgpOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuICF0aGlzLmhpZGVQaGFzZTtcbiAgICB9XG5cbiAgICBoaWRlKCk6IHZvaWQge1xuICAgICAgICB0aGlzLmhpZGVQaGFzZSA9IHRydWU7XG4gICAgICAgIHBoYXNlRmlsdGVyID0gcGhhc2VGaWx0ZXIuZmlsdGVyKGl0ZW0gPT4gaXRlbSAhPSB0aGlzLnBoYXNlKTtcbiAgICAgICAgdGhpcy5jbGFzc0xpc3QuYWRkKFwibGluZV90aHJvdWdoXCIpO1xuICAgIH1cblxuICAgIHNob3coKTogdm9pZCB7XG4gICAgICAgIHRoaXMuaGlkZVBoYXNlID0gZmFsc2U7XG4gICAgICAgIHBoYXNlRmlsdGVyLnB1c2godGhpcy5waGFzZSk7XG4gICAgICAgIHRoaXMuY2xhc3NMaXN0LnJlbW92ZShcImxpbmVfdGhyb3VnaFwiKTtcbiAgICB9XG5cbiAgICB1cGRhdGVQaGFzZUZpbHRlcigpOiB2b2lkIHtcbiAgICAgICAgcGhhc2VGaWx0ZXIuaW5jbHVkZXModGhpcy5waGFzZSkgPyB0aGlzLmhpZGUoKSA6IHRoaXMuc2hvdygpO1xuICAgIH1cblxuICAgIGNvbm5lY3RlZENhbGxiYWNrKCk6IHZvaWQge1xuICAgICAgICBpZiAodGhpcy5kYXRhc2V0W1wicGhhc2VcIl0pIHRoaXMucGhhc2UgPSB0aGlzLmRhdGFzZXRbXCJwaGFzZVwiXSBhcyBzdHJpbmc7XG4gICAgfVxufVxuXG5jbGFzcyBTeXN0b3JpU29ydEJ1dHRvbiBleHRlbmRzIEhUTUxFbGVtZW50IHtcbiAgICB0YWcgPSBcInN5cy1zb3J0LWJ1dHRvblwiO1xuXG4gICAgZ2V0IHR5cGUoKTogc3RyaW5nIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuZGF0YXNldFtcInR5cGVcIl0gfHwgXCJcIjtcbiAgICB9XG4gICAgc2V0IHR5cGUodHlwZTogc3RyaW5nKSB7XG4gICAgICAgIHRoaXMuZGF0YXNldFtcInR5cGVcIl0gPSB0eXBlO1xuICAgIH1cblxuICAgIGdldCByZXZlcnNlZCgpOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuZGF0YXNldFtcInJldmVyc2VkXCJdID09IFwidHJ1ZVwiO1xuICAgIH1cbiAgICBzZXQgcmV2ZXJzZWQocmV2ZXJzZWQ6IGJvb2xlYW4pIHtcbiAgICAgICAgcmV2ZXJzZWRcbiAgICAgICAgICAgID8gKHRoaXMuZGF0YXNldFtcInJldmVyc2VkXCJdID0gXCJ0cnVlXCIpXG4gICAgICAgICAgICA6ICh0aGlzLmRhdGFzZXRbXCJyZXZlcnNlZFwiXSA9IFwiZmFsc2VcIik7XG4gICAgfVxuXG4gICAgZ2V0IGFjdGl2ZSgpOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuY2xhc3NMaXN0LmNvbnRhaW5zKFwiYWN0aXZlXCIpO1xuICAgIH1cbiAgICBzZXQgYWN0aXZlKGFjdGl2ZTogYm9vbGVhbikge1xuICAgICAgICBhY3RpdmUgPyB0aGlzLmNsYXNzTGlzdC5hZGQoXCJhY3RpdmVcIikgOiB0aGlzLmNsYXNzTGlzdC5yZW1vdmUoXCJhY3RpdmVcIik7XG4gICAgfVxuXG4gICAgYWN0aXZhdGVFeGNsdXNpdmUoKTogdm9pZCB7XG4gICAgICAgIGNvbnN0IGJ0bnMgPSBBcnJheS5mcm9tKFxuICAgICAgICAgICAgKHRoaXMucGFyZW50RWxlbWVudCBhcyBIVE1MRGl2RWxlbWVudCkucXVlcnlTZWxlY3RvckFsbDxcbiAgICAgICAgICAgICAgICBTeXN0b3JpU29ydEJ1dHRvblxuICAgICAgICAgICAgPihcInN5cy1zb3J0LWJ1dHRvblwiKSxcbiAgICAgICAgKTtcbiAgICAgICAgZm9yIChjb25zdCBidG4gb2YgYnRucykge1xuICAgICAgICAgICAgYnRuLmFjdGl2ZSA9IGZhbHNlO1xuICAgICAgICB9XG4gICAgICAgIHRoaXMuYWN0aXZlID0gdHJ1ZTtcbiAgICAgICAgbG9jYWxTdG9yYWdlW1wic3lzLXNvcnQtYnV0dG9uXCJdID0gdGhpcy50eXBlO1xuICAgICAgICBsb2NhbFN0b3JhZ2VbXCJzeXMtc29ydC1idXR0b24tcmV2ZXJzZWRcIl0gPSB0aGlzLnJldmVyc2VkLnRvU3RyaW5nKCk7XG4gICAgfVxuXG4gICAgY29ubmVjdGVkQ2FsbGJhY2soKTogdm9pZCB7XG4gICAgICAgIGlmICh0aGlzLmRhdGFzZXRbXCJ0eXBlXCJdICE9IG51bGwpXG4gICAgICAgICAgICB0aGlzLnR5cGUgPSB0aGlzLmRhdGFzZXRbXCJ0eXBlXCJdIGFzIHN0cmluZztcbiAgICAgICAgaWYgKHRoaXMuZGF0YXNldFtcInJldmVyc2VkXCJdICE9IG51bGwpXG4gICAgICAgICAgICB0aGlzLnJldmVyc2VkID0gdGhpcy5kYXRhc2V0W1wicmV2ZXJzZWRcIl0gPT0gXCJ0cnVlXCI7XG4gICAgfVxufVxuXG5jbGFzcyBTeXN0b3JpUHJvamVjdFRpbGUgZXh0ZW5kcyBIVE1MRWxlbWVudCB7XG4gICAgdGFnID0gXCJzeXMtcHJvamVjdC10aWxlXCI7XG5cbiAgICBnZXQgaGlkZVByb2plY3RUaWxlKCk6IGJvb2xlYW4ge1xuICAgICAgICByZXR1cm4gdGhpcy5jbGFzc0xpc3QuY29udGFpbnMoXCJoaWRkZW5cIik7XG4gICAgfVxuICAgIHNldCBoaWRlUHJvamVjdFRpbGUoaGlkZVByb2plY3RUaWxlOiBib29sZWFuKSB7XG4gICAgICAgIGhpZGVQcm9qZWN0VGlsZVxuICAgICAgICAgICAgPyB0aGlzLmNsYXNzTGlzdC5hZGQoXCJoaWRkZW5cIilcbiAgICAgICAgICAgIDogdGhpcy5jbGFzc0xpc3QucmVtb3ZlKFwiaGlkZGVuXCIpO1xuICAgIH1cbn1cblxuY2xhc3MgU3lzdG9yaVdhcm5pbmdNZXNzYWdlIGV4dGVuZHMgSFRNTEVsZW1lbnQge1xuICAgIHRhZyA9IFwic3lzLXdhcm5pbmctbWVzc2FnZVwiO1xuXG4gICAgd2FyblBoYXNlRmlsdGVyZWRQcm9qZWN0cyhwaGFzZUZpbHRlcmVkUHJvamVjdHM6IG51bWJlcik6IHZvaWQge1xuICAgICAgICBpZiAocGhhc2VGaWx0ZXJlZFByb2plY3RzID4gMCkge1xuICAgICAgICAgICAgdGhpcy5jaGlsZHJlblswXS5pbm5lckhUTUwgPSAoZG9jdW1lbnQucXVlcnlTZWxlY3RvcihcbiAgICAgICAgICAgICAgICBcIiNzeXMtcGhhc2VGaWx0ZXJlZFByb2plY3RzLXRyYW5zbGF0ZWRcIixcbiAgICAgICAgICAgICkgYXMgSFRNTEVsZW1lbnQpLmlubmVyVGV4dDtcbiAgICAgICAgICAgIHRoaXMuY2xhc3NMaXN0LnJlbW92ZShcImhpZGRlblwiKTtcbiAgICAgICAgfVxuICAgIH1cblxuICAgIGdldCBoaWRlV2FybmluZ01lc3NhZ2UoKTogYm9vbGVhbiB7XG4gICAgICAgIHJldHVybiB0aGlzLmNsYXNzTGlzdC5jb250YWlucyhcImhpZGRlblwiKTtcbiAgICB9XG4gICAgc2V0IGhpZGVXYXJuaW5nTWVzc2FnZShoaWRlV2FybmluZ01lc3NhZ2U6IGJvb2xlYW4pIHtcbiAgICAgICAgaGlkZVdhcm5pbmdNZXNzYWdlXG4gICAgICAgICAgICA/IHRoaXMuY2xhc3NMaXN0LmFkZChcImhpZGRlblwiKVxuICAgICAgICAgICAgOiB0aGlzLmNsYXNzTGlzdC5yZW1vdmUoXCJoaWRkZW5cIik7XG4gICAgfVxufVxuXG5mdW5jdGlvbiBsb2FkTG9jYWxTdG9yYWdlKCk6IHZvaWQge1xuICAgIChkb2N1bWVudC5xdWVyeVNlbGVjdG9yKFwiI2ZpbHRlci1iYXJcIikgYXMgSFRNTEVsZW1lbnQpLmNsYXNzTGlzdC5yZW1vdmUoXG4gICAgICAgIFwiaGlkZGVuXCIsXG4gICAgKTtcbiAgICAoZG9jdW1lbnQucXVlcnlTZWxlY3RvcihcIiN0aWxlLWNvbnRhaW5lclwiKSBhcyBIVE1MRWxlbWVudCkuY2xhc3NMaXN0LnJlbW92ZShcbiAgICAgICAgXCJoaWRkZW5cIixcbiAgICApO1xufVxuXG53aW5kb3cuY3VzdG9tRWxlbWVudHMuZGVmaW5lKFwic3lzLXBoYXNlLWJ1dHRvblwiLCBTeXN0b3JpUGhhc2VCdXR0b24pO1xud2luZG93LmN1c3RvbUVsZW1lbnRzLmRlZmluZShcInN5cy1zb3J0LWJ1dHRvblwiLCBTeXN0b3JpU29ydEJ1dHRvbik7XG53aW5kb3cuY3VzdG9tRWxlbWVudHMuZGVmaW5lKFwic3lzLXByb2plY3QtdGlsZVwiLCBTeXN0b3JpUHJvamVjdFRpbGUpO1xud2luZG93LmN1c3RvbUVsZW1lbnRzLmRlZmluZShcInN5cy13YXJuaW5nLW1lc3NhZ2VcIiwgU3lzdG9yaVdhcm5pbmdNZXNzYWdlKTtcblxuLy8gYWRkIEV2ZW50IExpc3RlbmVyc1xuZm9yIChjb25zdCBidG4gb2YgZG9jdW1lbnQucXVlcnlTZWxlY3RvckFsbDxTeXN0b3JpU29ydEJ1dHRvbj4oXG4gICAgXCJzeXMtc29ydC1idXR0b25cIixcbikpIHtcbiAgICBidG4uYWRkRXZlbnRMaXN0ZW5lcihcImNsaWNrXCIsIHNvcnRQcm9qZWN0cyk7XG59XG5cbmZvciAoY29uc3QgYnRuIG9mIGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGw8U3lzdG9yaVBoYXNlQnV0dG9uPihcbiAgICBcInN5cy1waGFzZS1idXR0b25cIixcbikpIHtcbiAgICBidG4uYWRkRXZlbnRMaXN0ZW5lcihcImNsaWNrXCIsIHVwZGF0ZVBoYXNlRmlsdGVyKTtcbn1cblxuLy8gTG9hZCB1c2VyIChicm93c2VyKSBkYXRhXG5sb2FkTG9jYWxTdG9yYWdlKCk7XG4iXSwic291cmNlUm9vdCI6IiJ9