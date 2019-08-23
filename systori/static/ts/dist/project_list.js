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

/***/ "./src/project_list.ts":
/*!*****************************!*\
  !*** ./src/project_list.ts ***!
  \*****************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";

const filterBar = document.querySelector("#filter-bar");
const tileContainer = document.querySelector("#tile-container");
var PhaseOrder;
(function (PhaseOrder) {
    PhaseOrder[PhaseOrder["prospective"] = 0] = "prospective";
    PhaseOrder[PhaseOrder["tendering"] = 1] = "tendering";
    PhaseOrder[PhaseOrder["planning"] = 2] = "planning";
    PhaseOrder[PhaseOrder["executing"] = 3] = "executing";
    PhaseOrder[PhaseOrder["settlement"] = 4] = "settlement";
    PhaseOrder[PhaseOrder["warranty"] = 5] = "warranty";
    PhaseOrder[PhaseOrder["finished"] = 6] = "finished";
})(PhaseOrder || (PhaseOrder = {}));
var SortButtonType;
(function (SortButtonType) {
    SortButtonType["id"] = "id";
    SortButtonType["name"] = "name";
    SortButtonType["phase"] = "phase";
})(SortButtonType || (SortButtonType = {}));
class SystoriProjectTile extends HTMLElement {
    constructor() {
        super();
    }
    get pk() {
        console.log("hasdas");
        return Number(this.dataset["pk"]);
    }
    get name() {
        return this.dataset["name"];
    }
    get phase() {
        return (this.dataset["phase"] || PhaseOrder.prospective);
    }
    get hidden() {
        return this.dataset["hidden"] === "true";
    }
    set hide(hide) {
        this.dataset["hidden"] = hide.toString();
    }
    set show(hide) {
        this.dataset["hidden"] = hide.toString();
    }
}
class SystoriSortButton extends HTMLElement {
    constructor() {
        super();
        this.addEventListener("click", () => this.sortProjectTiles());
    }
    get type() {
        switch (this.dataset["type"]) {
            case "id":
                return SortButtonType.id;
            case "name":
                return SortButtonType.name;
            case "phase":
                return SortButtonType.phase;
            default:
                throw Error("Couldn't catch SortButtonType.");
        }
    }
    set type(type) {
        this.dataset["type"] = SortButtonType[type];
    }
    get reversed() {
        return this.dataset["reversed"] == "true";
    }
    set reversed(reversed) {
        reversed
            ? (this.dataset["reversed"] = "true")
            : (this.dataset["reversed"] = "false");
    }
    toggleReversed() {
        this.reversed = !this.reversed;
    }
    get active() {
        return this.classList.contains("active");
    }
    set active(active) {
        active ? this.classList.add("active") : this.classList.remove("active");
    }
    // adds class `active` to active button and removes it from all others.
    activateExclusive() {
        const btns = Array.from(document.querySelectorAll("sys-sort-button"));
        for (const btn of btns) {
            btn.active = false;
        }
        this.active = true;
    }
    sortProjectTiles() {
        this.toggleReversed();
        this.activateExclusive();
        const projectTiles = Array.from(document.querySelectorAll(".tile"));
        projectTiles.sort((a, b) => {
            if (this.type === "id") {
                if (this.reversed) {
                    return b.pk < a.pk ? -1 : 1;
                }
                else {
                    return a.pk < b.pk ? -1 : 1;
                }
            }
            else if (this.type === "name") {
                if (this.reversed) {
                    return a.name.localeCompare(b.name);
                }
                else {
                    return b.name.localeCompare(a.name);
                }
            }
            else if (this.type === "phase") {
                if (this.reversed) {
                    return PhaseOrder[b.phase] <= PhaseOrder[a.phase] ? -1 : 1;
                }
                else {
                    return PhaseOrder[a.phase] <= PhaseOrder[b.phase] ? -1 : 1;
                }
            }
            else {
                throw new Error("Unkown Button type.");
            }
        });
        if (tileContainer) {
            tileContainer.innerHTML = "";
            for (const tile of projectTiles) {
                tileContainer.appendChild(tile);
            }
        }
    }
}
class SystoriPhaseButton extends HTMLElement {
    constructor() {
        super();
        this.addEventListener("click", () => this.filterProjectTiles());
    }
    filterProjectTiles() {
        console.log("filtering!");
    }
}
customElements.define("sys-phase-button", SystoriPhaseButton);
customElements.define("sys-sort-button", SystoriSortButton);
customElements.define("sys-project-tile", SystoriProjectTile);
if (filterBar) {
    filterBar.classList.remove("hidden");
}
if (tileContainer) {
    tileContainer.classList.remove("hidden");
}


/***/ })

/******/ });
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8vd2VicGFjay9ib290c3RyYXAiLCJ3ZWJwYWNrOi8vLy4vc3JjL3Byb2plY3RfbGlzdC50cyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiO1FBQUE7UUFDQTs7UUFFQTtRQUNBOztRQUVBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBOztRQUVBO1FBQ0E7O1FBRUE7UUFDQTs7UUFFQTtRQUNBO1FBQ0E7OztRQUdBO1FBQ0E7O1FBRUE7UUFDQTs7UUFFQTtRQUNBO1FBQ0E7UUFDQSwwQ0FBMEMsZ0NBQWdDO1FBQzFFO1FBQ0E7O1FBRUE7UUFDQTtRQUNBO1FBQ0Esd0RBQXdELGtCQUFrQjtRQUMxRTtRQUNBLGlEQUFpRCxjQUFjO1FBQy9EOztRQUVBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQSx5Q0FBeUMsaUNBQWlDO1FBQzFFLGdIQUFnSCxtQkFBbUIsRUFBRTtRQUNySTtRQUNBOztRQUVBO1FBQ0E7UUFDQTtRQUNBLDJCQUEyQiwwQkFBMEIsRUFBRTtRQUN2RCxpQ0FBaUMsZUFBZTtRQUNoRDtRQUNBO1FBQ0E7O1FBRUE7UUFDQSxzREFBc0QsK0RBQStEOztRQUVySDtRQUNBOzs7UUFHQTtRQUNBOzs7Ozs7Ozs7Ozs7OztBQ2xGQSxNQUFNLFNBQVMsR0FBRyxRQUFRLENBQUMsYUFBYSxDQUFDLGFBQWEsQ0FBQyxDQUFDO0FBQ3hELE1BQU0sYUFBYSxHQUFHLFFBQVEsQ0FBQyxhQUFhLENBQUMsaUJBQWlCLENBQUMsQ0FBQztBQUNoRSxJQUFLLFVBUUo7QUFSRCxXQUFLLFVBQVU7SUFDWCx5REFBVztJQUNYLHFEQUFTO0lBQ1QsbURBQVE7SUFDUixxREFBUztJQUNULHVEQUFVO0lBQ1YsbURBQVE7SUFDUixtREFBUTtBQUNaLENBQUMsRUFSSSxVQUFVLEtBQVYsVUFBVSxRQVFkO0FBQ0QsSUFBSyxjQUlKO0FBSkQsV0FBSyxjQUFjO0lBQ2YsMkJB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LGtCQUFrQixFQUFFLGtCQUFrQixDQUFDLENBQUM7QUFDOUQsY0FBYyxDQUFDLE1BQU0sQ0FBQyxpQkFBaUIsRUFBRSxpQkFBaUIsQ0FBQyxDQUFDO0FBQzVELGNBQWMsQ0FBQyxNQUFNLENBQUMsa0JBQWtCLEVBQUUsa0JBQWtCLENBQUMsQ0FBQztBQUU5RCxJQUFJLFNBQVMsRUFBRTtJQUNYLFNBQVMsQ0FBQyxTQUFTLENBQUMsTUFBTSxDQUFDLFFBQVEsQ0FBQyxDQUFDO0NBQ3hDO0FBQ0QsSUFBSSxhQUFhLEVBQUU7SUFDZixhQUFhLENBQUMsU0FBUyxDQUFDLE1BQU0sQ0FBQyxRQUFRLENBQUMsQ0FBQztDQUM1QyIsImZpbGUiOiJwcm9qZWN0X2xpc3QuanMiLCJzb3VyY2VzQ29udGVudCI6WyIgXHQvLyBUaGUgbW9kdWxlIGNhY2hlXG4gXHR2YXIgaW5zdGFsbGVkTW9kdWxlcyA9IHt9O1xuXG4gXHQvLyBUaGUgcmVxdWlyZSBmdW5jdGlvblxuIFx0ZnVuY3Rpb24gX193ZWJwYWNrX3JlcXVpcmVfXyhtb2R1bGVJZCkge1xuXG4gXHRcdC8vIENoZWNrIGlmIG1vZHVsZSBpcyBpbiBjYWNoZVxuIFx0XHRpZihpbnN0YWxsZWRNb2R1bGVzW21vZHVsZUlkXSkge1xuIFx0XHRcdHJldHVybiBpbnN0YWxsZWRNb2R1bGVzW21vZHVsZUlkXS5leHBvcnRzO1xuIFx0XHR9XG4gXHRcdC8vIENyZWF0ZSBhIG5ldyBtb2R1bGUgKGFuZCBwdXQgaXQgaW50byB0aGUgY2FjaGUpXG4gXHRcdHZhciBtb2R1bGUgPSBpbnN0YWxsZWRNb2R1bGVzW21vZHVsZUlkXSA9IHtcbiBcdFx0XHRpOiBtb2R1bGVJZCxcbiBcdFx0XHRsOiBmYWxzZSxcbiBcdFx0XHRleHBvcnRzOiB7fVxuIFx0XHR9O1xuXG4gXHRcdC8vIEV4ZWN1dGUgdGhlIG1vZHVsZSBmdW5jdGlvblxuIFx0XHRtb2R1bGVzW21vZHVsZUlkXS5jYWxsKG1vZHVsZS5leHBvcnRzLCBtb2R1bGUsIG1vZHVsZS5leHBvcnRzLCBfX3dlYnBhY2tfcmVxdWlyZV9fKTtcblxuIFx0XHQvLyBGbGFnIHRoZSBtb2R1bGUgYXMgbG9hZGVkXG4gXHRcdG1vZHVsZS5sID0gdHJ1ZTtcblxuIFx0XHQvLyBSZXR1cm4gdGhlIGV4cG9ydHMgb2YgdGhlIG1vZHVsZVxuIFx0XHRyZXR1cm4gbW9kdWxlLmV4cG9ydHM7XG4gXHR9XG5cblxuIFx0Ly8gZXhwb3NlIHRoZSBtb2R1bGVzIG9iamVjdCAoX193ZWJwYWNrX21vZHVsZXNfXylcbiBcdF9fd2VicGFja19yZXF1aXJlX18ubSA9IG1vZHVsZXM7XG5cbiBcdC8vIGV4cG9zZSB0aGUgbW9kdWxlIGNhY2hlXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLmMgPSBpbnN0YWxsZWRNb2R1bGVzO1xuXG4gXHQvLyBkZWZpbmUgZ2V0dGVyIGZ1bmN0aW9uIGZvciBoYXJtb255IGV4cG9ydHNcbiBcdF9fd2VicGFja19yZXF1aXJlX18uZCA9IGZ1bmN0aW9uKGV4cG9ydHMsIG5hbWUsIGdldHRlcikge1xuIFx0XHRpZighX193ZWJwYWNrX3JlcXVpcmVfXy5vKGV4cG9ydHMsIG5hbWUpKSB7XG4gXHRcdFx0T2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIG5hbWUsIHsgZW51bWVyYWJsZTogdHJ1ZSwgZ2V0OiBnZXR0ZXIgfSk7XG4gXHRcdH1cbiBcdH07XG5cbiBcdC8vIGRlZmluZSBfX2VzTW9kdWxlIG9uIGV4cG9ydHNcbiBcdF9fd2VicGFja19yZXF1aXJlX18uciA9IGZ1bmN0aW9uKGV4cG9ydHMpIHtcbiBcdFx0aWYodHlwZW9mIFN5bWJvbCAhPT0gJ3VuZGVmaW5lZCcgJiYgU3ltYm9sLnRvU3RyaW5nVGFnKSB7XG4gXHRcdFx0T2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIFN5bWJvbC50b1N0cmluZ1RhZywgeyB2YWx1ZTogJ01vZHVsZScgfSk7XG4gXHRcdH1cbiBcdFx0T2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsICdfX2VzTW9kdWxlJywgeyB2YWx1ZTogdHJ1ZSB9KTtcbiBcdH07XG5cbiBcdC8vIGNyZWF0ZSBhIGZha2UgbmFtZXNwYWNlIG9iamVjdFxuIFx0Ly8gbW9kZSAmIDE6IHZhbHVlIGlzIGEgbW9kdWxlIGlkLCByZXF1aXJlIGl0XG4gXHQvLyBtb2RlICYgMjogbWVyZ2UgYWxsIHByb3BlcnRpZXMgb2YgdmFsdWUgaW50byB0aGUgbnNcbiBcdC8vIG1vZGUgJiA0OiByZXR1cm4gdmFsdWUgd2hlbiBhbHJlYWR5IG5zIG9iamVjdFxuIFx0Ly8gbW9kZSAmIDh8MTogYmVoYXZlIGxpa2UgcmVxdWlyZVxuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy50ID0gZnVuY3Rpb24odmFsdWUsIG1vZGUpIHtcbiBcdFx0aWYobW9kZSAmIDEpIHZhbHVlID0gX193ZWJwYWNrX3JlcXVpcmVfXyh2YWx1ZSk7XG4gXHRcdGlmKG1vZGUgJiA4KSByZXR1cm4gdmFsdWU7XG4gXHRcdGlmKChtb2RlICYgNCkgJiYgdHlwZW9mIHZhbHVlID09PSAnb2JqZWN0JyAmJiB2YWx1ZSAmJiB2YWx1ZS5fX2VzTW9kdWxlKSByZXR1cm4gdmFsdWU7XG4gXHRcdHZhciBucyA9IE9iamVjdC5jcmVhdGUobnVsbCk7XG4gXHRcdF9fd2VicGFja19yZXF1aXJlX18ucihucyk7XG4gXHRcdE9iamVjdC5kZWZpbmVQcm9wZXJ0eShucywgJ2RlZmF1bHQnLCB7IGVudW1lcmFibGU6IHRydWUsIHZhbHVlOiB2YWx1ZSB9KTtcbiBcdFx0aWYobW9kZSAmIDIgJiYgdHlwZW9mIHZhbHVlICE9ICdzdHJpbmcnKSBmb3IodmFyIGtleSBpbiB2YWx1ZSkgX193ZWJwYWNrX3JlcXVpcmVfXy5kKG5zLCBrZXksIGZ1bmN0aW9uKGtleSkgeyByZXR1cm4gdmFsdWVba2V5XTsgfS5iaW5kKG51bGwsIGtleSkpO1xuIFx0XHRyZXR1cm4gbnM7XG4gXHR9O1xuXG4gXHQvLyBnZXREZWZhdWx0RXhwb3J0IGZ1bmN0aW9uIGZvciBjb21wYXRpYmlsaXR5IHdpdGggbm9uLWhhcm1vbnkgbW9kdWxlc1xuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy5uID0gZnVuY3Rpb24obW9kdWxlKSB7XG4gXHRcdHZhciBnZXR0ZXIgPSBtb2R1bGUgJiYgbW9kdWxlLl9fZXNNb2R1bGUgP1xuIFx0XHRcdGZ1bmN0aW9uIGdldERlZmF1bHQoKSB7IHJldHVybiBtb2R1bGVbJ2RlZmF1bHQnXTsgfSA6XG4gXHRcdFx0ZnVuY3Rpb24gZ2V0TW9kdWxlRXhwb3J0cygpIHsgcmV0dXJuIG1vZHVsZTsgfTtcbiBcdFx0X193ZWJwYWNrX3JlcXVpcmVfXy5kKGdldHRlciwgJ2EnLCBnZXR0ZXIpO1xuIFx0XHRyZXR1cm4gZ2V0dGVyO1xuIFx0fTtcblxuIFx0Ly8gT2JqZWN0LnByb3RvdHlwZS5oYXNPd25Qcm9wZXJ0eS5jYWxsXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLm8gPSBmdW5jdGlvbihvYmplY3QsIHByb3BlcnR5KSB7IHJldHVybiBPYmplY3QucHJvdG90eXBlLmhhc093blByb3BlcnR5LmNhbGwob2JqZWN0LCBwcm9wZXJ0eSk7IH07XG5cbiBcdC8vIF9fd2VicGFja19wdWJsaWNfcGF0aF9fXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLnAgPSBcIlwiO1xuXG5cbiBcdC8vIExvYWQgZW50cnkgbW9kdWxlIGFuZCByZXR1cm4gZXhwb3J0c1xuIFx0cmV0dXJuIF9fd2VicGFja19yZXF1aXJlX18oX193ZWJwYWNrX3JlcXVpcmVfXy5zID0gXCIuL3NyYy9wcm9qZWN0X2xpc3QudHNcIik7XG4iLCJjb25zdCBmaWx0ZXJCYXIgPSBkb2N1bWVudC5xdWVyeVNlbGVjdG9yKFwiI2ZpbHRlci1iYXJcIik7XG5jb25zdCB0aWxlQ29udGFpbmVyID0gZG9jdW1lbnQucXVlcnlTZWxlY3RvcihcIiN0aWxlLWNvbnRhaW5lclwiKTtcbmVudW0gUGhhc2VPcmRlciB7XG4gICAgcHJvc3BlY3RpdmUsXG4gICAgdGVuZGVyaW5nLFxuICAgIHBsYW5uaW5nLFxuICAgIGV4ZWN1dGluZyxcbiAgICBzZXR0bGVtZW50LFxuICAgIHdhcnJhbnR5LFxuICAgIGZpbmlzaGVkLFxufVxuZW51bSBTb3J0QnV0dG9uVHlwZSB7XG4gICAgaWQgPSBcImlkXCIsXG4gICAgbmFtZSA9IFwibmFtZVwiLFxuICAgIHBoYXNlID0gXCJwaGFzZVwiLFxufVxuXG5jbGFzcyBTeXN0b3JpUHJvamVjdFRpbGUgZXh0ZW5kcyBIVE1MRWxlbWVudCB7XG4gICAgY29uc3RydWN0b3IoKSB7XG4gICAgICAgIHN1cGVyKCk7XG4gICAgfVxuICAgIGdldCBwaygpOiBudW1iZXIge1xuICAgICAgICBjb25zb2xlLmxvZyhcImhhc2Rhc1wiKTtcbiAgICAgICAgcmV0dXJuIE51bWJlcih0aGlzLmRhdGFzZXRbXCJwa1wiXSEpO1xuICAgIH1cbiAgICBnZXQgbmFtZSgpOiBzdHJpbmcge1xuICAgICAgICByZXR1cm4gdGhpcy5kYXRhc2V0W1wibmFtZVwiXSE7XG4gICAgfVxuICAgIGdldCBwaGFzZSgpOiBQaGFzZU9yZGVyIHtcbiAgICAgICAgcmV0dXJuICh0aGlzLmRhdGFzZXRbXCJwaGFzZVwiXSB8fCBQaGFzZU9yZGVyLnByb3NwZWN0aXZlKSBhcyBQaGFzZU9yZGVyO1xuICAgIH1cblxuICAgIGdldCBoaWRkZW4oKTogYm9vbGVhbiB7XG4gICAgICAgIHJldHVybiB0aGlzLmRhdGFzZXRbXCJoaWRkZW5cIl0gPT09IFwidHJ1ZVwiO1xuICAgIH1cbiAgICBzZXQgaGlkZShoaWRlOiBib29sZWFuKSB7XG4gICAgICAgIHRoaXMuZGF0YXNldFtcImhpZGRlblwiXSA9IGhpZGUudG9TdHJpbmcoKTtcbiAgICB9XG4gICAgc2V0IHNob3coaGlkZTogYm9vbGVhbikge1xuICAgICAgICB0aGlzLmRhdGFzZXRbXCJoaWRkZW5cIl0gPSBoaWRlLnRvU3RyaW5nKCk7XG4gICAgfVxufVxuXG5jbGFzcyBTeXN0b3JpU29ydEJ1dHRvbiBleHRlbmRzIEhUTUxFbGVtZW50IHtcbiAgICBjb25zdHJ1Y3RvcigpIHtcbiAgICAgICAgc3VwZXIoKTtcbiAgICAgICAgdGhpcy5hZGRFdmVudExpc3RlbmVyKFwiY2xpY2tcIiwgKCkgPT4gdGhpcy5zb3J0UHJvamVjdFRpbGVzKCkpO1xuICAgIH1cbiAgICBnZXQgdHlwZSgpOiBTb3J0QnV0dG9uVHlwZSB7XG4gICAgICAgIHN3aXRjaCAodGhpcy5kYXRhc2V0W1widHlwZVwiXSkge1xuICAgICAgICAgICAgY2FzZSBcImlkXCI6XG4gICAgICAgICAgICAgICAgcmV0dXJuIFNvcnRCdXR0b25UeXBlLmlkO1xuICAgICAgICAgICAgY2FzZSBcIm5hbWVcIjpcbiAgICAgICAgICAgICAgICByZXR1cm4gU29ydEJ1dHRvblR5cGUubmFtZTtcbiAgICAgICAgICAgIGNhc2UgXCJwaGFzZVwiOlxuICAgICAgICAgICAgICAgIHJldHVybiBTb3J0QnV0dG9uVHlwZS5waGFzZTtcbiAgICAgICAgICAgIGRlZmF1bHQ6XG4gICAgICAgICAgICAgICAgdGhyb3cgRXJyb3IoXCJDb3VsZG4ndCBjYXRjaCBTb3J0QnV0dG9uVHlwZS5cIik7XG4gICAgICAgIH1cbiAgICB9XG4gICAgc2V0IHR5cGUodHlwZTogU29ydEJ1dHRvblR5cGUpIHtcbiAgICAgICAgdGhpcy5kYXRhc2V0W1widHlwZVwiXSA9IFNvcnRCdXR0b25UeXBlW3R5cGVdO1xuICAgIH1cblxuICAgIGdldCByZXZlcnNlZCgpOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuZGF0YXNldFtcInJldmVyc2VkXCJdID09IFwidHJ1ZVwiO1xuICAgIH1cbiAgICBzZXQgcmV2ZXJzZWQocmV2ZXJzZWQ6IGJvb2xlYW4pIHtcbiAgICAgICAgcmV2ZXJzZWRcbiAgICAgICAgICAgID8gKHRoaXMuZGF0YXNldFtcInJldmVyc2VkXCJdID0gXCJ0cnVlXCIpXG4gICAgICAgICAgICA6ICh0aGlzLmRhdGFzZXRbXCJyZXZlcnNlZFwiXSA9IFwiZmFsc2VcIik7XG4gICAgfVxuICAgIHRvZ2dsZVJldmVyc2VkKCk6IHZvaWQge1xuICAgICAgICB0aGlzLnJldmVyc2VkID0gIXRoaXMucmV2ZXJzZWQ7XG4gICAgfVxuXG4gICAgZ2V0IGFjdGl2ZSgpOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuY2xhc3NMaXN0LmNvbnRhaW5zKFwiYWN0aXZlXCIpO1xuICAgIH1cbiAgICBzZXQgYWN0aXZlKGFjdGl2ZTogYm9vbGVhbikge1xuICAgICAgICBhY3RpdmUgPyB0aGlzLmNsYXNzTGlzdC5hZGQoXCJhY3RpdmVcIikgOiB0aGlzLmNsYXNzTGlzdC5yZW1vdmUoXCJhY3RpdmVcIik7XG4gICAgfVxuXG4gICAgLy8gYWRkcyBjbGFzcyBgYWN0aXZlYCB0byBhY3RpdmUgYnV0dG9uIGFuZCByZW1vdmVzIGl0IGZyb20gYWxsIG90aGVycy5cbiAgICBhY3RpdmF0ZUV4Y2x1c2l2ZSgpOiB2b2lkIHtcbiAgICAgICAgY29uc3QgYnRuczogU3lzdG9yaVNvcnRCdXR0b25bXSA9IEFycmF5LmZyb20oXG4gICAgICAgICAgICBkb2N1bWVudC5xdWVyeVNlbGVjdG9yQWxsKFwic3lzLXNvcnQtYnV0dG9uXCIpLFxuICAgICAgICApO1xuICAgICAgICBmb3IgKGNvbnN0IGJ0biBvZiBidG5zKSB7XG4gICAgICAgICAgICBidG4uYWN0aXZlID0gZmFsc2U7XG4gICAgICAgIH1cbiAgICAgICAgdGhpcy5hY3RpdmUgPSB0cnVlO1xuICAgIH1cblxuICAgIHNvcnRQcm9qZWN0VGlsZXMoKTogdm9pZCB7XG4gICAgICAgIHRoaXMudG9nZ2xlUmV2ZXJzZWQoKTtcbiAgICAgICAgdGhpcy5hY3RpdmF0ZUV4Y2x1c2l2ZSgpO1xuXG4gICAgICAgIGNvbnN0IHByb2plY3RUaWxlcyA9IEFycmF5LmZyb20oXG4gICAgICAgICAgICBkb2N1bWVudC5xdWVyeVNlbGVjdG9yQWxsPFN5c3RvcmlQcm9qZWN0VGlsZT4oXCIudGlsZVwiKSxcbiAgICAgICAgKTtcblxuICAgICAgICBwcm9qZWN0VGlsZXMuc29ydCgoYSwgYikgPT4ge1xuICAgICAgICAgICAgaWYgKHRoaXMudHlwZSA9PT0gXCJpZFwiKSB7XG4gICAgICAgICAgICAgICAgaWYgKHRoaXMucmV2ZXJzZWQpIHtcbiAgICAgICAgICAgICAgICAgICAgcmV0dXJuIGIucGsgPCBhLnBrID8gLTEgOiAxO1xuICAgICAgICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICAgICAgICAgIHJldHVybiBhLnBrIDwgYi5wayA/IC0xIDogMTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9IGVsc2UgaWYgKHRoaXMudHlwZSA9PT0gXCJuYW1lXCIpIHtcbiAgICAgICAgICAgICAgICBpZiAodGhpcy5yZXZlcnNlZCkge1xuICAgICAgICAgICAgICAgICAgICByZXR1cm4gYS5uYW1lLmxvY2FsZUNvbXBhcmUoYi5uYW1lKTtcbiAgICAgICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgICAgICByZXR1cm4gYi5uYW1lLmxvY2FsZUNvbXBhcmUoYS5uYW1lKTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9IGVsc2UgaWYgKHRoaXMudHlwZSA9PT0gXCJwaGFzZVwiKSB7XG4gICAgICAgICAgICAgICAgaWYgKHRoaXMucmV2ZXJzZWQpIHtcbiAgICAgICAgICAgICAgICAgICAgcmV0dXJuIFBoYXNlT3JkZXJbYi5waGFzZV0gPD0gUGhhc2VPcmRlclthLnBoYXNlXSA/IC0xIDogMTtcbiAgICAgICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgICAgICByZXR1cm4gUGhhc2VPcmRlclthLnBoYXNlXSA8PSBQaGFzZU9yZGVyW2IucGhhc2VdID8gLTEgOiAxO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICAgICAgdGhyb3cgbmV3IEVycm9yKFwiVW5rb3duIEJ1dHRvbiB0eXBlLlwiKTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfSk7XG5cbiAgICAgICAgaWYgKHRpbGVDb250YWluZXIpIHtcbiAgICAgICAgICAgIHRpbGVDb250YWluZXIuaW5uZXJIVE1MID0gXCJcIjtcbiAgICAgICAgICAgIGZvciAoY29uc3QgdGlsZSBvZiBwcm9qZWN0VGlsZXMpIHtcbiAgICAgICAgICAgICAgICB0aWxlQ29udGFpbmVyLmFwcGVuZENoaWxkKHRpbGUpO1xuICAgICAgICAgICAgfVxuICAgICAgICB9XG4gICAgfVxufVxuXG5jbGFzcyBTeXN0b3JpUGhhc2VCdXR0b24gZXh0ZW5kcyBIVE1MRWxlbWVudCB7XG4gICAgY29uc3RydWN0b3IoKSB7XG4gICAgICAgIHN1cGVyKCk7XG4gICAgICAgIHRoaXMuYWRkRXZlbnRMaXN0ZW5lcihcImNsaWNrXCIsICgpID0+IHRoaXMuZmlsdGVyUHJvamVjdFRpbGVzKCkpO1xuICAgIH1cblxuICAgIGZpbHRlclByb2plY3RUaWxlcygpOiB2b2lkIHtcbiAgICAgICAgY29uc29sZS5sb2coXCJmaWx0ZXJpbmchXCIpO1xuICAgIH1cbn1cblxuY3VzdG9tRWxlbWVudHMuZGVmaW5lKFwic3lzLXBoYXNlLWJ1dHRvblwiLCBTeXN0b3JpUGhhc2VCdXR0b24pO1xuY3VzdG9tRWxlbWVudHMuZGVmaW5lKFwic3lzLXNvcnQtYnV0dG9uXCIsIFN5c3RvcmlTb3J0QnV0dG9uKTtcbmN1c3RvbUVsZW1lbnRzLmRlZmluZShcInN5cy1wcm9qZWN0LXRpbGVcIiwgU3lzdG9yaVByb2plY3RUaWxlKTtcblxuaWYgKGZpbHRlckJhcikge1xuICAgIGZpbHRlckJhci5jbGFzc0xpc3QucmVtb3ZlKFwiaGlkZGVuXCIpO1xufVxuaWYgKHRpbGVDb250YWluZXIpIHtcbiAgICB0aWxlQ29udGFpbmVyLmNsYXNzTGlzdC5yZW1vdmUoXCJoaWRkZW5cIik7XG59XG4iXSwic291cmNlUm9vdCI6IiJ9