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


// const searchRequestFired = false;
// const attemptMade = false;
// let searchMatches: Array<number>;
let phaseFilter;
var PhaseOrder;
(function (PhaseOrder) {
    PhaseOrder["prospective"] = "prospective";
    PhaseOrder["tendering"] = "tendering";
    PhaseOrder["planning"] = "planning";
    PhaseOrder["executing"] = "executing";
    PhaseOrder["settlement"] = "settlement";
    PhaseOrder["warranty"] = "warranty";
    PhaseOrder["finished"] = "finished";
})(PhaseOrder || (PhaseOrder = {}));
function sortProjects(e) {
    if (e == null)
        return;
    let lookup = new Map();
    // const i = 0;
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
        for (const key in PhaseOrder) {
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
    let lastMoved = null;
    for (const key of sortedKeys) {
        if (lastMoved == null) {
            console.log(`lastMoved == ${lastMoved} with key == ${key}`);
            lastMoved = lookup.get(key);
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
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8vd2VicGFjay9ib290c3RyYXAiLCJ3ZWJwYWNrOi8vLy4vbm9kZV9tb2R1bGVzL25hdHVyYWwtc29ydC9kaXN0L25hdHVyYWwtc29ydC5qcyIsIndlYnBhY2s6Ly8vLi9zcmMvbGliL211bHRpbWFwLnRzIiwid2VicGFjazovLy8uL3NyYy9wcm9qZWN0X2xpc3QudHMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IjtRQUFBO1FBQ0E7O1FBRUE7UUFDQTs7UUFFQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTs7UUFFQTtRQUNBOztRQUVBO1FBQ0E7O1FBRUE7UUFDQTtRQUNBOzs7UUFHQTtRQUNBOztRQUVBO1FBQ0E7O1FBRUE7UUFDQTtRQUNBO1FBQ0EsMENBQTBDLGdDQUFnQztRQUMxRTtRQUNBOztRQUVBO1FBQ0E7UUFDQTtRQUNBLHdEQUF3RCxrQkFBa0I7UUFDMUU7UUFDQSxpREFBaUQsY0FBYztRQUMvRDs7UUFFQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0EseUNBQXlDLGlDQUFpQztRQUMxRSxnSEFBZ0gsbUJBQW1CLEVBQUU7UUFDckk7UUFDQTs7UUFFQTtRQUNBO1FBQ0E7UUFDQSwyQkFBMkIsMEJBQTBCLEVBQUU7UUFDdkQsaUNBQWlDLGVBQWU7UUFDaEQ7UUFDQTtRQUNBOztRQUVBO1FBQ0Esc0RBQXNELCtEQUErRDs7UUFFckg7UUFDQTs7O1FBR0E7UUFDQTs7Ozs7Ozs7Ozs7O0FDbEZBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUFFQSxrREFBa0Q7QUFDbEQ7O0FBRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FBRUE7QUFDQTtBQUNBLHlFQUF5RSxJQUFJLFNBQVMsSUFBSSxTQUFTLElBQUksbUJBQW1CLEVBQUU7QUFDNUg7QUFD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QWtCLEVBQUUsa0JBQWtCLENBQUMsQ0FBQztBQUNyRSxNQUFNLENBQUMsY0FBYyxDQUFDLE1BQU0sQ0FBQyxpQkFBaUIsRUFBRSxpQkFBaUIsQ0FBQyxDQUFDO0FBQ25FLE1BQU0sQ0FBQyxjQUFjLENBQUMsTUFBTSxDQUFDLGtCQUFrQixFQUFFLGtCQUFrQixDQUFDLENBQUM7QUFDckUsTUFBTSxDQUFDLGNBQWMsQ0FBQyxNQUFNLENBQUMscUJBQXFCLEVBQUUscUJBQXFCLENBQUMsQ0FBQztBQUUzRSxzQkFBc0I7QUFDdEIsS0FBSyxNQUFNLEdBQUcsSUFBSSxRQUFRLENBQUMsZ0JBQWdCLENBQ3ZDLGlCQUFpQixDQUNwQixFQUFFO0lBQ0MsR0FBRyxDQUFDLGdCQUFnQixDQUFDLE9BQU8sRUFBRSxZQUFZLENBQUMsQ0FBQztDQUMvQztBQUVELEtBQUssTUFBTSxHQUFHLElBQUksUUFBUSxDQUFDLGdCQUFnQixDQUN2QyxrQkFBa0IsQ0FDckIsRUFBRTtJQUNDLEdBQUcsQ0FBQyxnQkFBZ0IsQ0FBQyxPQUFPLEVBQUUsaUJBQWlCLENBQUMsQ0FBQztDQUNwRDtBQUVELDJCQUEyQjtBQUMzQixnQkFBZ0IsRUFBRSxDQUFDIiwiZmlsZSI6InByb2plY3RfbGlzdC5qcyIsInNvdXJjZXNDb250ZW50IjpbIiBcdC8vIFRoZSBtb2R1bGUgY2FjaGVcbiBcdHZhciBpbnN0YWxsZWRNb2R1bGVzID0ge307XG5cbiBcdC8vIFRoZSByZXF1aXJlIGZ1bmN0aW9uXG4gXHRmdW5jdGlvbiBfX3dlYnBhY2tfcmVxdWlyZV9fKG1vZHVsZUlkKSB7XG5cbiBcdFx0Ly8gQ2hlY2sgaWYgbW9kdWxlIGlzIGluIGNhY2hlXG4gXHRcdGlmKGluc3RhbGxlZE1vZHVsZXNbbW9kdWxlSWRdKSB7XG4gXHRcdFx0cmV0dXJuIGluc3RhbGxlZE1vZHVsZXNbbW9kdWxlSWRdLmV4cG9ydHM7XG4gXHRcdH1cbiBcdFx0Ly8gQ3JlYXRlIGEgbmV3IG1vZHVsZSAoYW5kIHB1dCBpdCBpbnRvIHRoZSBjYWNoZSlcbiBcdFx0dmFyIG1vZHVsZSA9IGluc3RhbGxlZE1vZHVsZXNbbW9kdWxlSWRdID0ge1xuIFx0XHRcdGk6IG1vZHVsZUlkLFxuIFx0XHRcdGw6IGZhbHNlLFxuIFx0XHRcdGV4cG9ydHM6IHt9XG4gXHRcdH07XG5cbiBcdFx0Ly8gRXhlY3V0ZSB0aGUgbW9kdWxlIGZ1bmN0aW9uXG4gXHRcdG1vZHVsZXNbbW9kdWxlSWRdLmNhbGwobW9kdWxlLmV4cG9ydHMsIG1vZHVsZSwgbW9kdWxlLmV4cG9ydHMsIF9fd2VicGFja19yZXF1aXJlX18pO1xuXG4gXHRcdC8vIEZsYWcgdGhlIG1vZHVsZSBhcyBsb2FkZWRcbiBcdFx0bW9kdWxlLmwgPSB0cnVlO1xuXG4gXHRcdC8vIFJldHVybiB0aGUgZXhwb3J0cyBvZiB0aGUgbW9kdWxlXG4gXHRcdHJldHVybiBtb2R1bGUuZXhwb3J0cztcbiBcdH1cblxuXG4gXHQvLyBleHBvc2UgdGhlIG1vZHVsZXMgb2JqZWN0IChfX3dlYnBhY2tfbW9kdWxlc19fKVxuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy5tID0gbW9kdWxlcztcblxuIFx0Ly8gZXhwb3NlIHRoZSBtb2R1bGUgY2FjaGVcbiBcdF9fd2VicGFja19yZXF1aXJlX18uYyA9IGluc3RhbGxlZE1vZHVsZXM7XG5cbiBcdC8vIGRlZmluZSBnZXR0ZXIgZnVuY3Rpb24gZm9yIGhhcm1vbnkgZXhwb3J0c1xuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy5kID0gZnVuY3Rpb24oZXhwb3J0cywgbmFtZSwgZ2V0dGVyKSB7XG4gXHRcdGlmKCFfX3dlYnBhY2tfcmVxdWlyZV9fLm8oZXhwb3J0cywgbmFtZSkpIHtcbiBcdFx0XHRPYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgbmFtZSwgeyBlbnVtZXJhYmxlOiB0cnVlLCBnZXQ6IGdldHRlciB9KTtcbiBcdFx0fVxuIFx0fTtcblxuIFx0Ly8gZGVmaW5lIF9fZXNNb2R1bGUgb24gZXhwb3J0c1xuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy5yID0gZnVuY3Rpb24oZXhwb3J0cykge1xuIFx0XHRpZih0eXBlb2YgU3ltYm9sICE9PSAndW5kZWZpbmVkJyAmJiBTeW1ib2wudG9TdHJpbmdUYWcpIHtcbiBcdFx0XHRPYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgU3ltYm9sLnRvU3RyaW5nVGFnLCB7IHZhbHVlOiAnTW9kdWxlJyB9KTtcbiBcdFx0fVxuIFx0XHRPYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgJ19fZXNNb2R1bGUnLCB7IHZhbHVlOiB0cnVlIH0pO1xuIFx0fTtcblxuIFx0Ly8gY3JlYXRlIGEgZmFrZSBuYW1lc3BhY2Ugb2JqZWN0XG4gXHQvLyBtb2RlICYgMTogdmFsdWUgaXMgYSBtb2R1bGUgaWQsIHJlcXVpcmUgaXRcbiBcdC8vIG1vZGUgJiAyOiBtZXJnZSBhbGwgcHJvcGVydGllcyBvZiB2YWx1ZSBpbnRvIHRoZSBuc1xuIFx0Ly8gbW9kZSAmIDQ6IHJldHVybiB2YWx1ZSB3aGVuIGFscmVhZHkgbnMgb2JqZWN0XG4gXHQvLyBtb2RlICYgOHwxOiBiZWhhdmUgbGlrZSByZXF1aXJlXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLnQgPSBmdW5jdGlvbih2YWx1ZSwgbW9kZSkge1xuIFx0XHRpZihtb2RlICYgMSkgdmFsdWUgPSBfX3dlYnBhY2tfcmVxdWlyZV9fKHZhbHVlKTtcbiBcdFx0aWYobW9kZSAmIDgpIHJldHVybiB2YWx1ZTtcbiBcdFx0aWYoKG1vZGUgJiA0KSAmJiB0eXBlb2YgdmFsdWUgPT09ICdvYmplY3QnICYmIHZhbHVlICYmIHZhbHVlLl9fZXNNb2R1bGUpIHJldHVybiB2YWx1ZTtcbiBcdFx0dmFyIG5zID0gT2JqZWN0LmNyZWF0ZShudWxsKTtcbiBcdFx0X193ZWJwYWNrX3JlcXVpcmVfXy5yKG5zKTtcbiBcdFx0T2JqZWN0LmRlZmluZVByb3BlcnR5KG5zLCAnZGVmYXVsdCcsIHsgZW51bWVyYWJsZTogdHJ1ZSwgdmFsdWU6IHZhbHVlIH0pO1xuIFx0XHRpZihtb2RlICYgMiAmJiB0eXBlb2YgdmFsdWUgIT0gJ3N0cmluZycpIGZvcih2YXIga2V5IGluIHZhbHVlKSBfX3dlYnBhY2tfcmVxdWlyZV9fLmQobnMsIGtleSwgZnVuY3Rpb24oa2V5KSB7IHJldHVybiB2YWx1ZVtrZXldOyB9LmJpbmQobnVsbCwga2V5KSk7XG4gXHRcdHJldHVybiBucztcbiBcdH07XG5cbiBcdC8vIGdldERlZmF1bHRFeHBvcnQgZnVuY3Rpb24gZm9yIGNvbXBhdGliaWxpdHkgd2l0aCBub24taGFybW9ueSBtb2R1bGVzXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLm4gPSBmdW5jdGlvbihtb2R1bGUpIHtcbiBcdFx0dmFyIGdldHRlciA9IG1vZHVsZSAmJiBtb2R1bGUuX19lc01vZHVsZSA/XG4gXHRcdFx0ZnVuY3Rpb24gZ2V0RGVmYXVsdCgpIHsgcmV0dXJuIG1vZHVsZVsnZGVmYXVsdCddOyB9IDpcbiBcdFx0XHRmdW5jdGlvbiBnZXRNb2R1bGVFeHBvcnRzKCkgeyByZXR1cm4gbW9kdWxlOyB9O1xuIFx0XHRfX3dlYnBhY2tfcmVxdWlyZV9fLmQoZ2V0dGVyLCAnYScsIGdldHRlcik7XG4gXHRcdHJldHVybiBnZXR0ZXI7XG4gXHR9O1xuXG4gXHQvLyBPYmplY3QucHJvdG90eXBlLmhhc093blByb3BlcnR5LmNhbGxcbiBcdF9fd2VicGFja19yZXF1aXJlX18ubyA9IGZ1bmN0aW9uKG9iamVjdCwgcHJvcGVydHkpIHsgcmV0dXJuIE9iamVjdC5wcm90b3R5cGUuaGFzT3duUHJvcGVydHkuY2FsbChvYmplY3QsIHByb3BlcnR5KTsgfTtcblxuIFx0Ly8gX193ZWJwYWNrX3B1YmxpY19wYXRoX19cbiBcdF9fd2VicGFja19yZXF1aXJlX18ucCA9IFwiXCI7XG5cblxuIFx0Ly8gTG9hZCBlbnRyeSBtb2R1bGUgYW5kIHJldHVybiBleHBvcnRzXG4gXHRyZXR1cm4gX193ZWJwYWNrX3JlcXVpcmVfXyhfX3dlYnBhY2tfcmVxdWlyZV9fLnMgPSBcIi4vc3JjL3Byb2plY3RfbGlzdC50c1wiKTtcbiIsIi8qIVxuICogbmF0dXJhbC1zb3J0LmpzXG4gKiA9PT09PT09PT09PT09PT1cbiAqIFNvcnRpbmcgd2l0aCBzdXBwb3J0IGZvciBudW1iZXJzLCBkYXRlcywgdW5pY29kZSBhbmQgbW9yZS5cbiAqXG4gKiBodHRwOi8vZ2l0aHViLmNvbS9zdHVkaW8tYjEyL25hdHVyYWwtc29ydFxuICogTUlUIExpY2Vuc2UsIMKpIFN0dWRpbyBCMTIgR21iSCAyMDE0XG4gKlxuICovLypcbiAqXG4gKiBJZGVhIGJ5IERhdmUgS29lbGxlXG4gKiBPcmlnaW5hbCBpbXBsZW1lbnRhdGlvbiBieSBKaW0gUGFsbWVyXG4gKiBNb2RpZmllZCBieSBUb21layBXaXN6bmlld3NraVxuICpcbiAqL1xuXG52YXIgbmF0dXJhbFNvcnQgPSBmdW5jdGlvbiBuYXR1cmFsU29ydCAob3B0aW9ucykgeyAndXNlIHN0cmljdCc7XG4gIGlmICghb3B0aW9ucykgb3B0aW9ucyA9IHt9O1xuXG4gIHJldHVybiBmdW5jdGlvbihhLCBiKSB7XG4gICAgdmFyIEVRVUFMID0gMDtcbiAgICB2YXIgR1JFQVRFUiA9IChvcHRpb25zLmRpcmVjdGlvbiA9PSAnZGVzYycgP1xuICAgICAgLTEgOlxuICAgICAgMVxuICAgICk7XG4gICAgdmFyIFNNQUxMRVIgPSAtR1JFQVRFUjtcblxuICAgIHZhciByZSA9IC8oXi0/WzAtOV0rKFxcLj9bMC05XSopW2RmXT9lP1swLTldPyR8XjB4WzAtOWEtZl0rJHxbMC05XSspL2dpO1xuICAgIHZhciBzcmUgPSAvKF5bIF0qfFsgXSokKS9nO1xuICAgIHZhciBkcmUgPSAvKF4oW1xcdyBdKyw/W1xcdyBdKyk/W1xcdyBdKyw/W1xcdyBdK1xcZCs6XFxkKyg6XFxkKyk/W1xcdyBdP3xeXFxkezEsNH1bXFwvXFwtXVxcZHsxLDR9W1xcL1xcLV1cXGR7MSw0fXxeXFx3KywgXFx3KyBcXGQrLCBcXGR7NH0pLztcbiAgICB2YXIgaHJlID0gL14weFswLTlhLWZdKyQvaTtcbiAgICB2YXIgb3JlID0gL14wLztcblxuICAgIHZhciBub3JtYWxpemUgPSBmdW5jdGlvbiBub3JtYWxpemUgKHZhbHVlKSB7XG4gICAgICB2YXIgc3RyaW5nID0gJycgKyB2YWx1ZTtcbiAgICAgIHJldHVybiAob3B0aW9ucy5jYXNlU2Vuc2l0aXZlID9cbiAgICAgICAgc3RyaW5nIDpcbiAgICAgICAgc3RyaW5nLnRvTG93ZXJDYXNlKClcbiAgICAgICk7XG4gICAgfTtcblxuICAgIC8vIE5vcm1hbGl6ZSB2YWx1ZXMgdG8gc3RyaW5nc1xuICAgIHZhciB4ID0gbm9ybWFsaXplKGEpLnJlcGxhY2Uoc3JlLCAnJykgfHwgJyc7XG4gICAgdmFyIHkgPSBub3JtYWxpemUoYikucmVwbGFjZShzcmUsICcnKSB8fCAnJztcblxuICAgIC8vIGNodW5rL3Rva2VuaXplXG4gICAgdmFyIHhOID0geC5yZXBsYWNlKHJlLCAnXFwwJDFcXDAnKS5yZXBsYWNlKC9cXDAkLywnJykucmVwbGFjZSgvXlxcMC8sJycpLnNwbGl0KCdcXDAnKTtcbiAgICB2YXIgeU4gPSB5LnJlcGxhY2UocmUsICdcXDAkMVxcMCcpLnJlcGxhY2UoL1xcMCQvLCcnKS5yZXBsYWNlKC9eXFwwLywnJykuc3BsaXQoJ1xcMCcpO1xuXG4gICAgLy8gUmV0dXJuIGltbWVkaWF0ZWx5IGlmIGF0IGxlYXN0IG9uZSBvZiB0aGUgdmFsdWVzIGlzIGVtcHR5LlxuICAgIGlmICgheCAmJiAheSkgcmV0dXJuIEVRVUFMO1xuICAgIGlmICgheCAmJiAgeSkgcmV0dXJuIEdSRUFURVI7XG4gICAgaWYgKCB4ICYmICF5KSByZXR1cm4gU01BTExFUjtcblxuICAgIC8vIG51bWVyaWMsIGhleCBvciBkYXRlIGRldGVjdGlvblxuICAgIHZhciB4RCA9IHBhcnNlSW50KHgubWF0Y2goaHJlKSkgfHwgKHhOLmxlbmd0aCAhPSAxICYmIHgubWF0Y2goZHJlKSAmJiBEYXRlLnBhcnNlKHgpKTtcbiAgICB2YXIgeUQgPSBwYXJzZUludCh5Lm1hdGNoKGhyZSkpIHx8IHhEICYmIHkubWF0Y2goZHJlKSAmJiBEYXRlLnBhcnNlKHkpIHx8IG51bGw7XG4gICAgdmFyIG9GeE5jTCwgb0Z5TmNMO1xuXG4gICAgLy8gZmlyc3QgdHJ5IGFuZCBzb3J0IEhleCBjb2RlcyBvciBEYXRlc1xuICAgIGlmICh5RCkge1xuICAgICAgaWYgKCB4RCA8IHlEICkgcmV0dXJuIFNNQUxMRVI7XG4gICAgICBlbHNlIGlmICggeEQgPiB5RCApIHJldHVybiBHUkVBVEVSO1xuICAgIH1cblxuICAgIC8vIG5hdHVyYWwgc29ydGluZyB0aHJvdWdoIHNwbGl0IG51bWVyaWMgc3RyaW5ncyBhbmQgZGVmYXVsdCBzdHJpbmdzXG4gICAgZm9yICh2YXIgY0xvYz0wLCBudW1TPU1hdGgubWF4KHhOLmxlbmd0aCwgeU4ubGVuZ3RoKTsgY0xvYyA8IG51bVM7IGNMb2MrKykge1xuXG4gICAgICAvLyBmaW5kIGZsb2F0cyBub3Qgc3RhcnRpbmcgd2l0aCAnMCcsIHN0cmluZyBvciAwIGlmIG5vdCBkZWZpbmVkIChDbGludCBQcmllc3QpXG4gICAgICBvRnhOY0wgPSAhKHhOW2NMb2NdIHx8ICcnKS5tYXRjaChvcmUpICYmIHBhcnNlRmxvYXQoeE5bY0xvY10pIHx8IHhOW2NMb2NdIHx8IDA7XG4gICAgICBvRnlOY0wgPSAhKHlOW2NMb2NdIHx8ICcnKS5tYXRjaChvcmUpICYmIHBhcnNlRmxvYXQoeU5bY0xvY10pIHx8IHlOW2NMb2NdIHx8IDA7XG5cbiAgICAgIC8vIGhhbmRsZSBudW1lcmljIHZzIHN0cmluZyBjb21wYXJpc29uIC0gbnVtYmVyIDwgc3RyaW5nIC0gKEt5bGUgQWRhbXMpXG4gICAgICBpZiAoaXNOYU4ob0Z4TmNMKSAhPT0gaXNOYU4ob0Z5TmNMKSkgcmV0dXJuIChpc05hTihvRnhOY0wpKSA/IEdSRUFURVIgOiBTTUFMTEVSO1xuXG4gICAgICAvLyByZWx5IG9uIHN0cmluZyBjb21wYXJpc29uIGlmIGRpZmZlcmVudCB0eXBlcyAtIGkuZS4gJzAyJyA8IDIgIT0gJzAyJyA8ICcyJ1xuICAgICAgZWxzZSBpZiAodHlwZW9mIG9GeE5jTCAhPT0gdHlwZW9mIG9GeU5jTCkge1xuICAgICAgICBvRnhOY0wgKz0gJyc7XG4gICAgICAgIG9GeU5jTCArPSAnJztcbiAgICAgIH1cblxuICAgICAgaWYgKG9GeE5jTCA8IG9GeU5jTCkgcmV0dXJuIFNNQUxMRVI7XG4gICAgICBpZiAob0Z4TmNMID4gb0Z5TmNMKSByZXR1cm4gR1JFQVRFUjtcbiAgICB9XG5cbiAgICByZXR1cm4gRVFVQUw7XG4gIH07XG59O1xuXG4oZnVuY3Rpb24gKHJvb3QsIGZhY3RvcnkpIHtcbiAgaWYgKHR5cGVvZiBleHBvcnRzID09PSAnb2JqZWN0Jykge1xuICAgIG1vZHVsZS5leHBvcnRzID0gZmFjdG9yeSgpO1xuICB9IGVsc2Uge1xuICAgIHJvb3QubmF0dXJhbFNvcnQgPSBmYWN0b3J5KCk7XG4gIH1cbn0odGhpcywgZnVuY3Rpb24gKCkge1xuXG4gIHJldHVybiBuYXR1cmFsU29ydDtcblxufSkpO1xuIiwiLyoqXG4gKiBAYXV0aG9yIEpvcmRhbiBMdXlrZSA8am9yZGFubHV5a2VAZ21haWwuY29tPlxuICovXG5cbmV4cG9ydCBpbnRlcmZhY2UgTXVsdGltYXA8SywgVj4ge1xuICAgIGNsZWFyKCk6IHZvaWQ7XG4gICAgY29udGFpbnNLZXkoa2V5OiBLKTogYm9vbGVhbjtcbiAgICBjb250YWluc1ZhbHVlKHZhbHVlOiBWKTogYm9vbGVhbjtcbiAgICBjb250YWluc0VudHJ5KGtleTogSywgdmFsdWU6IFYpOiBib29sZWFuO1xuICAgIGRlbGV0ZShrZXk6IEssIHZhbHVlPzogVik6IGJvb2xlYW47XG4gICAgZW50cmllczogTXVsdGltYXBFbnRyeTxLLCBWPltdO1xuICAgIGdldChrZXk6IEspOiBWW107XG4gICAga2V5cygpOiBLW107XG4gICAgcHV0KGtleTogSywgdmFsdWU6IFYpOiBNdWx0aW1hcEVudHJ5PEssIFY+W107XG59XG5cbmV4cG9ydCBjbGFzcyBBcnJheUxpc3RNdWx0aW1hcDxLLCBWPiBpbXBsZW1lbnRzIE11bHRpbWFwPEssIFY+IHtcbiAgICBwcml2YXRlIF9lbnRyaWVzOiBNdWx0aW1hcEVudHJ5PEssIFY+W10gPSBbXTtcblxuICAgIHB1YmxpYyBjbGVhcigpOiB2b2lkIHtcbiAgICAgICAgdGhpcy5fZW50cmllcyA9IFtdO1xuICAgIH1cblxuICAgIHB1YmxpYyBjb250YWluc0tleShrZXk6IEspOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuX2VudHJpZXMuZmlsdGVyKGVudHJ5ID0+IGVudHJ5LmtleSA9PSBrZXkpLmxlbmd0aCA+IDA7XG4gICAgfVxuXG4gICAgcHVibGljIGNvbnRhaW5zVmFsdWUodmFsdWU6IFYpOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuX2VudHJpZXMuZmlsdGVyKGVudHJ5ID0+IGVudHJ5LnZhbHVlID09IHZhbHVlKS5sZW5ndGggPiAwO1xuICAgIH1cblxuICAgIHB1YmxpYyBjb250YWluc0VudHJ5KGtleTogSywgdmFsdWU6IFYpOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuIChcbiAgICAgICAgICAgIHRoaXMuX2VudHJpZXMuZmlsdGVyKFxuICAgICAgICAgICAgICAgIGVudHJ5ID0+IGVudHJ5LmtleSA9PSBrZXkgJiYgZW50cnkudmFsdWUgPT0gdmFsdWUsXG4gICAgICAgICAgICApLmxlbmd0aCA+IDBcbiAgICAgICAgKTtcbiAgICB9XG5cbiAgICBwdWJsaWMgZGVsZXRlKGtleTogSywgdmFsdWU/OiBWKTogYm9vbGVhbiB7XG4gICAgICAgIGNvbnN0IHRlbXAgPSB0aGlzLl9lbnRyaWVzO1xuICAgICAgICB0aGlzLl9lbnRyaWVzID0gdGhpcy5fZW50cmllcy5maWx0ZXIoZW50cnkgPT4ge1xuICAgICAgICAgICAgaWYgKHZhbHVlKSByZXR1cm4gZW50cnkua2V5ICE9IGtleSB8fCBlbnRyeS52YWx1ZSAhPSB2YWx1ZTtcbiAgICAgICAgICAgIHJldHVybiBlbnRyeS5rZXkgIT0ga2V5O1xuICAgICAgICB9KTtcbiAgICAgICAgcmV0dXJuIHRlbXAubGVuZ3RoICE9IHRoaXMuX2VudHJpZXMubGVuZ3RoO1xuICAgIH1cblxuICAgIHB1YmxpYyBnZXQgZW50cmllcygpOiBNdWx0aW1hcEVudHJ5PEssIFY+W10ge1xuICAgICAgICByZXR1cm4gdGhpcy5fZW50cmllcztcbiAgICB9XG5cbiAgICBwdWJsaWMgZ2V0KGtleTogSyk6IFZbXSB7XG4gICAgICAgIHJldHVybiB0aGlzLl9lbnRyaWVzXG4gICAgICAgICAgICAuZmlsdGVyKGVudHJ5ID0+IGVudHJ5LmtleSA9PSBrZXkpXG4gICAgICAgICAgICAubWFwKGVudHJ5ID0+IGVudHJ5LnZhbHVlKTtcbiAgICB9XG5cbiAgICBwdWJsaWMga2V5cygpOiBLW10ge1xuICAgICAgICByZXR1cm4gQXJyYXkuZnJvbShuZXcgU2V0KHRoaXMuX2VudHJpZXMubWFwKGVudHJ5ID0+IGVudHJ5LmtleSkpKTtcbiAgICB9XG5cbiAgICBwdWJsaWMgcHV0KGtleTogSywgdmFsdWU6IFYpOiBNdWx0aW1hcEVudHJ5PEssIFY+W10ge1xuICAgICAgICB0aGlzLl9lbnRyaWVzLnB1c2gobmV3IE11bHRpbWFwRW50cnkoa2V5LCB2YWx1ZSkpO1xuICAgICAgICByZXR1cm4gdGhpcy5fZW50cmllcztcbiAgICB9XG59XG5cbmNsYXNzIE11bHRpbWFwRW50cnk8SywgVj4ge1xuICAgIGNvbnN0cnVjdG9yKHJlYWRvbmx5IGtleTogSywgcmVhZG9ubHkgdmFsdWU6IFYpIHt9XG59XG4iLCJpbXBvcnQgeyBBcnJheUxpc3RNdWx0aW1hcCwgTXVsdGltYXAgfSBmcm9tIFwiQHN5c3RvcmkvbGliL211bHRpbWFwXCI7XG5pbXBvcnQgbmF0dXJhbFNvcnQgZnJvbSBcIm5hdHVyYWwtc29ydFwiO1xuXG4vLyBjb25zdCBzZWFyY2hSZXF1ZXN0RmlyZWQgPSBmYWxzZTtcbi8vIGNvbnN0IGF0dGVtcHRNYWRlID0gZmFsc2U7XG4vLyBsZXQgc2VhcmNoTWF0Y2hlczogQXJyYXk8bnVtYmVyPjtcbmxldCBwaGFzZUZpbHRlcjogQXJyYXk8c3RyaW5nPjtcbmVudW0gUGhhc2VPcmRlciB7XG4gICAgcHJvc3BlY3RpdmUgPSBcInByb3NwZWN0aXZlXCIsXG4gICAgdGVuZGVyaW5nID0gXCJ0ZW5kZXJpbmdcIixcbiAgICBwbGFubmluZyA9IFwicGxhbm5pbmdcIixcbiAgICBleGVjdXRpbmcgPSBcImV4ZWN1dGluZ1wiLFxuICAgIHNldHRsZW1lbnQgPSBcInNldHRsZW1lbnRcIixcbiAgICB3YXJyYW50eSA9IFwid2FycmFudHlcIixcbiAgICBmaW5pc2hlZCA9IFwiZmluaXNoZWRcIixcbn1cblxuZnVuY3Rpb24gc29ydFByb2plY3RzKGU6IEV2ZW50KTogdm9pZCB7XG4gICAgaWYgKGUgPT0gbnVsbCkgcmV0dXJuO1xuICAgIGxldCBsb29rdXA6IE1hcDxzdHJpbmcgfCBudW1iZXIsIFN5c3RvcmlQcm9qZWN0VGlsZT4gPSBuZXcgTWFwKCk7XG4gICAgLy8gY29uc3QgaSA9IDA7XG5cbiAgICBjb25zdCBidG4gPSBlLnRhcmdldCBhcyBTeXN0b3JpU29ydEJ1dHRvbjtcbiAgICBidG4uYWN0aXZhdGVFeGNsdXNpdmUoKTtcblxuICAgIGlmIChidG4udHlwZSA9PSBcImlkXCIpIHtcbiAgICAgICAgQXJyYXkuZnJvbShkb2N1bWVudC5xdWVyeVNlbGVjdG9yQWxsPFN5c3RvcmlQcm9qZWN0VGlsZT4oXCIudGlsZVwiKSkubWFwKFxuICAgICAgICAgICAgZSA9PiBsb29rdXAuc2V0KHBhcnNlSW50KGUuZGF0YXNldFtcInBrXCJdIHx8IFwiMFwiKSwgZSksXG4gICAgICAgICk7XG4gICAgfSBlbHNlIGlmIChidG4udHlwZSA9PSBcIm5hbWVcIikge1xuICAgICAgICBBcnJheS5mcm9tKGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGw8U3lzdG9yaVByb2plY3RUaWxlPihcIi50aWxlXCIpKS5tYXAoXG4gICAgICAgICAgICBlID0+IGxvb2t1cC5zZXQoZS5kYXRhc2V0W1wibmFtZVwiXSB8fCBcIlwiLCBlKSxcbiAgICAgICAgKTtcbiAgICB9IGVsc2UgaWYgKGJ0bi50eXBlID09IFwicGhhc2VcIikge1xuICAgICAgICBjb25zdCBsb29rdXAyOiBNdWx0aW1hcDxzdHJpbmcsIEhUTUxFbGVtZW50PiA9IG5ldyBBcnJheUxpc3RNdWx0aW1hcCgpO1xuICAgICAgICBsb29rdXAgPSBuZXcgTWFwKCk7XG4gICAgICAgIEFycmF5LmZyb20oZG9jdW1lbnQucXVlcnlTZWxlY3RvckFsbDxTeXN0b3JpUHJvamVjdFRpbGU+KFwiLnRpbGVcIikpLm1hcChcbiAgICAgICAgICAgIGUgPT4gbG9va3VwMi5wdXQoZS5kYXRhc2V0W1wicGhhc2VcIl0gfHwgXCJcIiwgZSksXG4gICAgICAgICk7XG4gICAgICAgIGZvciAoY29uc3Qga2V5IGluIFBoYXNlT3JkZXIpIHtcbiAgICAgICAgICAgIC8vIGZvciAobGV0IGVsZW1lbnQgb2YgbG9va3VwMltrZXldKSB7XG4gICAgICAgICAgICAvLyAgICAgY29uc29sZS5sb2coZWxlbWVudCk7XG4gICAgICAgICAgICAvLyB9XG4gICAgICAgICAgICBjb25zb2xlLmxvZyhrZXkpO1xuICAgICAgICB9XG4gICAgfVxuXG4gICAgbGV0IHNvcnRlZEtleXM6IEFycmF5PHN0cmluZyB8IG51bWJlcj4gPSBBcnJheS5mcm9tKGxvb2t1cC5rZXlzKCkpLnNvcnQoXG4gICAgICAgIG5hdHVyYWxTb3J0KCksXG4gICAgKTtcbiAgICBpZiAoYnRuLnJldmVyc2VkID09IHRydWUpIHtcbiAgICAgICAgc29ydGVkS2V5cyA9IHNvcnRlZEtleXMucmV2ZXJzZSgpO1xuICAgICAgICBidG4ucmV2ZXJzZWQgPSBmYWxzZTtcbiAgICB9IGVsc2UgaWYgKGJ0bi5yZXZlcnNlZCA9PSBmYWxzZSkge1xuICAgICAgICBidG4ucmV2ZXJzZWQgPSB0cnVlO1xuICAgIH1cblxuICAgIGxldCBsYXN0TW92ZWQgPSBudWxsO1xuXG4gICAgZm9yIChjb25zdCBrZXkgb2Ygc29ydGVkS2V5cykge1xuICAgICAgICBpZiAobGFzdE1vdmVkID09IG51bGwpIHtcbiAgICAgICAgICAgIGNvbnNvbGUubG9nKGBsYXN0TW92ZWQgPT0gJHtsYXN0TW92ZWR9IHdpdGgga2V5ID09ICR7a2V5fWApO1xuICAgICAgICAgICAgbGFzdE1vdmVkID0gbG9va3VwLmdldChrZXkpO1xuICAgICAgICAgICAgY29udGludWU7XG4gICAgICAgIH1cbiAgICAgICAgLy9sYXN0TW92ZWQuaW5zZXJ0QWRqYWNlbnRFbGVtZW50KFwiYWZ0ZXJlbmRcIiwgbG9va3VwW2tleV0pO1xuICAgICAgICAvL2xhc3RfbW92ZWQgPSBsb29rdXBba2V5XTtcbiAgICB9XG59XG5cbmZ1bmN0aW9uIGZpbHRlclByb2plY3RzKCk6IHZvaWQge1xuICAgIGNvbnN0IHdhcm5pbmcgPSBkb2N1bWVudC5xdWVyeVNlbGVjdG9yKFxuICAgICAgICBcInN5cy13YXJuaW5nLW1lc3NhZ2VcIixcbiAgICApIGFzIFN5c3RvcmlXYXJuaW5nTWVzc2FnZTtcbiAgICB3YXJuaW5nLmhpZGVXYXJuaW5nTWVzc2FnZSA9IHRydWU7XG5cbiAgICBjb25zdCBwcm9qZWN0cyA9IGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGw8U3lzdG9yaVByb2plY3RUaWxlPihcIi50aWxlXCIpO1xuICAgIGZvciAoY29uc3QgcHJvamVjdCBvZiBwcm9qZWN0cykge1xuICAgICAgICBwcm9qZWN0LmNsYXNzTGlzdC5hZGQoXCJoaWRkZW5cIik7XG4gICAgfVxufVxuXG5mdW5jdGlvbiB1cGRhdGVQaGFzZUZpbHRlcihlOiBFdmVudCk6IHZvaWQge1xuICAgIGlmIChlID09IHVuZGVmaW5lZCkgcmV0dXJuO1xuICAgIGNvbnN0IGJ0biA9IGUudGFyZ2V0IGFzIFN5c3RvcmlQaGFzZUJ1dHRvbjtcbiAgICBidG4udXBkYXRlUGhhc2VGaWx0ZXIoKTtcbiAgICBsb2NhbFN0b3JhZ2VbXCJwaGFzZUZpbHRlclwiXSA9IEpTT04uc3RyaW5naWZ5KHsgcGhhc2VGaWx0ZXIgfSk7XG4gICAgZmlsdGVyUHJvamVjdHMoKTtcbn1cblxuY2xhc3MgU3lzdG9yaVBoYXNlQnV0dG9uIGV4dGVuZHMgSFRNTEVsZW1lbnQge1xuICAgIHRhZyA9IFwic3lzLXBoYXNlLWJ1dHRvblwiO1xuXG4gICAgZ2V0IHBoYXNlKCk6IHN0cmluZyB7XG4gICAgICAgIHJldHVybiB0aGlzLmRhdGFzZXRbXCJwaGFzZVwiXSB8fCBcIlwiO1xuICAgIH1cbiAgICBzZXQgcGhhc2UocGhhc2U6IHN0cmluZykge1xuICAgICAgICB0aGlzLmRhdGFzZXRbXCJwaGFzZVwiXSA9IHBoYXNlO1xuICAgIH1cblxuICAgIGdldCBoaWRlUGhhc2UoKTogYm9vbGVhbiB7XG4gICAgICAgIHJldHVybiB0aGlzLmRhdGFzZXRbXCJoaWRlLXBoYXNlXCJdID09IFwidHJ1ZVwiO1xuICAgIH1cbiAgICBzZXQgaGlkZVBoYXNlKGhpZGVQaGFzZTogYm9vbGVhbikge1xuICAgICAgICBoaWRlUGhhc2VcbiAgICAgICAgICAgID8gKHRoaXMuZGF0YXNldFtcImhpZGUtcGhhc2VcIl0gPSBcInRydWVcIilcbiAgICAgICAgICAgIDogKHRoaXMuZGF0YXNldFtcImhpZGUtcGhhc2VcIl0gPSBcImZhbHNlXCIpO1xuICAgIH1cbiAgICBnZXQgdmlzaWJsZVBoYXNlKCk6IGJvb2xlYW4ge1xuICAgICAgICByZXR1cm4gIXRoaXMuaGlkZVBoYXNlO1xuICAgIH1cblxuICAgIGhpZGUoKTogdm9pZCB7XG4gICAgICAgIHRoaXMuaGlkZVBoYXNlID0gdHJ1ZTtcbiAgICAgICAgcGhhc2VGaWx0ZXIgPSBwaGFzZUZpbHRlci5maWx0ZXIoaXRlbSA9PiBpdGVtICE9IHRoaXMucGhhc2UpO1xuICAgICAgICB0aGlzLmNsYXNzTGlzdC5hZGQoXCJsaW5lX3Rocm91Z2hcIik7XG4gICAgfVxuXG4gICAgc2hvdygpOiB2b2lkIHtcbiAgICAgICAgdGhpcy5oaWRlUGhhc2UgPSBmYWxzZTtcbiAgICAgICAgcGhhc2VGaWx0ZXIucHVzaCh0aGlzLnBoYXNlKTtcbiAgICAgICAgdGhpcy5jbGFzc0xpc3QucmVtb3ZlKFwibGluZV90aHJvdWdoXCIpO1xuICAgIH1cblxuICAgIHVwZGF0ZVBoYXNlRmlsdGVyKCk6IHZvaWQge1xuICAgICAgICBwaGFzZUZpbHRlci5pbmNsdWRlcyh0aGlzLnBoYXNlKSA/IHRoaXMuaGlkZSgpIDogdGhpcy5zaG93KCk7XG4gICAgfVxuXG4gICAgY29ubmVjdGVkQ2FsbGJhY2soKTogdm9pZCB7XG4gICAgICAgIGlmICh0aGlzLmRhdGFzZXRbXCJwaGFzZVwiXSkgdGhpcy5waGFzZSA9IHRoaXMuZGF0YXNldFtcInBoYXNlXCJdIGFzIHN0cmluZztcbiAgICB9XG59XG5cbmNsYXNzIFN5c3RvcmlTb3J0QnV0dG9uIGV4dGVuZHMgSFRNTEVsZW1lbnQge1xuICAgIHRhZyA9IFwic3lzLXNvcnQtYnV0dG9uXCI7XG5cbiAgICBnZXQgdHlwZSgpOiBzdHJpbmcge1xuICAgICAgICByZXR1cm4gdGhpcy5kYXRhc2V0W1widHlwZVwiXSB8fCBcIlwiO1xuICAgIH1cbiAgICBzZXQgdHlwZSh0eXBlOiBzdHJpbmcpIHtcbiAgICAgICAgdGhpcy5kYXRhc2V0W1widHlwZVwiXSA9IHR5cGU7XG4gICAgfVxuXG4gICAgZ2V0IHJldmVyc2VkKCk6IGJvb2xlYW4ge1xuICAgICAgICByZXR1cm4gdGhpcy5kYXRhc2V0W1wicmV2ZXJzZWRcIl0gPT0gXCJ0cnVlXCI7XG4gICAgfVxuICAgIHNldCByZXZlcnNlZChyZXZlcnNlZDogYm9vbGVhbikge1xuICAgICAgICByZXZlcnNlZFxuICAgICAgICAgICAgPyAodGhpcy5kYXRhc2V0W1wicmV2ZXJzZWRcIl0gPSBcInRydWVcIilcbiAgICAgICAgICAgIDogKHRoaXMuZGF0YXNldFtcInJldmVyc2VkXCJdID0gXCJmYWxzZVwiKTtcbiAgICB9XG5cbiAgICBnZXQgYWN0aXZlKCk6IGJvb2xlYW4ge1xuICAgICAgICByZXR1cm4gdGhpcy5jbGFzc0xpc3QuY29udGFpbnMoXCJhY3RpdmVcIik7XG4gICAgfVxuICAgIHNldCBhY3RpdmUoYWN0aXZlOiBib29sZWFuKSB7XG4gICAgICAgIGFjdGl2ZSA/IHRoaXMuY2xhc3NMaXN0LmFkZChcImFjdGl2ZVwiKSA6IHRoaXMuY2xhc3NMaXN0LnJlbW92ZShcImFjdGl2ZVwiKTtcbiAgICB9XG5cbiAgICBhY3RpdmF0ZUV4Y2x1c2l2ZSgpOiB2b2lkIHtcbiAgICAgICAgY29uc3QgYnRucyA9IEFycmF5LmZyb20oXG4gICAgICAgICAgICAodGhpcy5wYXJlbnRFbGVtZW50IGFzIEhUTUxEaXZFbGVtZW50KS5xdWVyeVNlbGVjdG9yQWxsPFxuICAgICAgICAgICAgICAgIFN5c3RvcmlTb3J0QnV0dG9uXG4gICAgICAgICAgICA+KFwic3lzLXNvcnQtYnV0dG9uXCIpLFxuICAgICAgICApO1xuICAgICAgICBmb3IgKGNvbnN0IGJ0biBvZiBidG5zKSB7XG4gICAgICAgICAgICBidG4uYWN0aXZlID0gZmFsc2U7XG4gICAgICAgIH1cbiAgICAgICAgdGhpcy5hY3RpdmUgPSB0cnVlO1xuICAgICAgICBsb2NhbFN0b3JhZ2VbXCJzeXMtc29ydC1idXR0b25cIl0gPSB0aGlzLnR5cGU7XG4gICAgICAgIGxvY2FsU3RvcmFnZVtcInN5cy1zb3J0LWJ1dHRvbi1yZXZlcnNlZFwiXSA9IHRoaXMucmV2ZXJzZWQudG9TdHJpbmcoKTtcbiAgICB9XG5cbiAgICBjb25uZWN0ZWRDYWxsYmFjaygpOiB2b2lkIHtcbiAgICAgICAgaWYgKHRoaXMuZGF0YXNldFtcInR5cGVcIl0gIT0gbnVsbClcbiAgICAgICAgICAgIHRoaXMudHlwZSA9IHRoaXMuZGF0YXNldFtcInR5cGVcIl0gYXMgc3RyaW5nO1xuICAgICAgICBpZiAodGhpcy5kYXRhc2V0W1wicmV2ZXJzZWRcIl0gIT0gbnVsbClcbiAgICAgICAgICAgIHRoaXMucmV2ZXJzZWQgPSB0aGlzLmRhdGFzZXRbXCJyZXZlcnNlZFwiXSA9PSBcInRydWVcIjtcbiAgICB9XG59XG5cbmNsYXNzIFN5c3RvcmlQcm9qZWN0VGlsZSBleHRlbmRzIEhUTUxFbGVtZW50IHtcbiAgICB0YWcgPSBcInN5cy1wcm9qZWN0LXRpbGVcIjtcblxuICAgIGdldCBoaWRlUHJvamVjdFRpbGUoKTogYm9vbGVhbiB7XG4gICAgICAgIHJldHVybiB0aGlzLmNsYXNzTGlzdC5jb250YWlucyhcImhpZGRlblwiKTtcbiAgICB9XG4gICAgc2V0IGhpZGVQcm9qZWN0VGlsZShoaWRlUHJvamVjdFRpbGU6IGJvb2xlYW4pIHtcbiAgICAgICAgaGlkZVByb2plY3RUaWxlXG4gICAgICAgICAgICA/IHRoaXMuY2xhc3NMaXN0LmFkZChcImhpZGRlblwiKVxuICAgICAgICAgICAgOiB0aGlzLmNsYXNzTGlzdC5yZW1vdmUoXCJoaWRkZW5cIik7XG4gICAgfVxufVxuXG5jbGFzcyBTeXN0b3JpV2FybmluZ01lc3NhZ2UgZXh0ZW5kcyBIVE1MRWxlbWVudCB7XG4gICAgdGFnID0gXCJzeXMtd2FybmluZy1tZXNzYWdlXCI7XG5cbiAgICB3YXJuUGhhc2VGaWx0ZXJlZFByb2plY3RzKHBoYXNlRmlsdGVyZWRQcm9qZWN0czogbnVtYmVyKTogdm9pZCB7XG4gICAgICAgIGlmIChwaGFzZUZpbHRlcmVkUHJvamVjdHMgPiAwKSB7XG4gICAgICAgICAgICB0aGlzLmNoaWxkcmVuWzBdLmlubmVySFRNTCA9IChkb2N1bWVudC5xdWVyeVNlbGVjdG9yKFxuICAgICAgICAgICAgICAgIFwiI3N5cy1waGFzZUZpbHRlcmVkUHJvamVjdHMtdHJhbnNsYXRlZFwiLFxuICAgICAgICAgICAgKSBhcyBIVE1MRWxlbWVudCkuaW5uZXJUZXh0O1xuICAgICAgICAgICAgdGhpcy5jbGFzc0xpc3QucmVtb3ZlKFwiaGlkZGVuXCIpO1xuICAgICAgICB9XG4gICAgfVxuXG4gICAgZ2V0IGhpZGVXYXJuaW5nTWVzc2FnZSgpOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuY2xhc3NMaXN0LmNvbnRhaW5zKFwiaGlkZGVuXCIpO1xuICAgIH1cbiAgICBzZXQgaGlkZVdhcm5pbmdNZXNzYWdlKGhpZGVXYXJuaW5nTWVzc2FnZTogYm9vbGVhbikge1xuICAgICAgICBoaWRlV2FybmluZ01lc3NhZ2VcbiAgICAgICAgICAgID8gdGhpcy5jbGFzc0xpc3QuYWRkKFwiaGlkZGVuXCIpXG4gICAgICAgICAgICA6IHRoaXMuY2xhc3NMaXN0LnJlbW92ZShcImhpZGRlblwiKTtcbiAgICB9XG59XG5cbmZ1bmN0aW9uIGxvYWRMb2NhbFN0b3JhZ2UoKTogdm9pZCB7XG4gICAgKGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3IoXCIjZmlsdGVyLWJhclwiKSBhcyBIVE1MRWxlbWVudCkuY2xhc3NMaXN0LnJlbW92ZShcbiAgICAgICAgXCJoaWRkZW5cIixcbiAgICApO1xuICAgIChkb2N1bWVudC5xdWVyeVNlbGVjdG9yKFwiI3RpbGUtY29udGFpbmVyXCIpIGFzIEhUTUxFbGVtZW50KS5jbGFzc0xpc3QucmVtb3ZlKFxuICAgICAgICBcImhpZGRlblwiLFxuICAgICk7XG59XG5cbndpbmRvdy5jdXN0b21FbGVtZW50cy5kZWZpbmUoXCJzeXMtcGhhc2UtYnV0dG9uXCIsIFN5c3RvcmlQaGFzZUJ1dHRvbik7XG53aW5kb3cuY3VzdG9tRWxlbWVudHMuZGVmaW5lKFwic3lzLXNvcnQtYnV0dG9uXCIsIFN5c3RvcmlTb3J0QnV0dG9uKTtcbndpbmRvdy5jdXN0b21FbGVtZW50cy5kZWZpbmUoXCJzeXMtcHJvamVjdC10aWxlXCIsIFN5c3RvcmlQcm9qZWN0VGlsZSk7XG53aW5kb3cuY3VzdG9tRWxlbWVudHMuZGVmaW5lKFwic3lzLXdhcm5pbmctbWVzc2FnZVwiLCBTeXN0b3JpV2FybmluZ01lc3NhZ2UpO1xuXG4vLyBhZGQgRXZlbnQgTGlzdGVuZXJzXG5mb3IgKGNvbnN0IGJ0biBvZiBkb2N1bWVudC5xdWVyeVNlbGVjdG9yQWxsPFN5c3RvcmlTb3J0QnV0dG9uPihcbiAgICBcInN5cy1zb3J0LWJ1dHRvblwiLFxuKSkge1xuICAgIGJ0bi5hZGRFdmVudExpc3RlbmVyKFwiY2xpY2tcIiwgc29ydFByb2plY3RzKTtcbn1cblxuZm9yIChjb25zdCBidG4gb2YgZG9jdW1lbnQucXVlcnlTZWxlY3RvckFsbDxTeXN0b3JpUGhhc2VCdXR0b24+KFxuICAgIFwic3lzLXBoYXNlLWJ1dHRvblwiLFxuKSkge1xuICAgIGJ0bi5hZGRFdmVudExpc3RlbmVyKFwiY2xpY2tcIiwgdXBkYXRlUGhhc2VGaWx0ZXIpO1xufVxuXG4vLyBMb2FkIHVzZXIgKGJyb3dzZXIpIGRhdGFcbmxvYWRMb2NhbFN0b3JhZ2UoKTtcbiJdLCJzb3VyY2VSb290IjoiIn0=