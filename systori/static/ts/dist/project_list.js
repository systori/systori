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
class SystoriProjectTile extends HTMLDivElement {
    constructor() {
        super();
    }
    get pk() {
        return Number(this.dataset["pk"] || "0");
    }
    get name() {
        return this.dataset["name"] || "unknown";
    }
    get phase() {
        return (this.dataset["phase"] || PhaseOrder.prospective);
    }
}
function sortProjectTiles(e) {
    const btn = e.target;
    if (!btn)
        throw new Error(`Expected SystoriSortButton as EventTarget but got ${e.target}.`);
    const projectTiles = Array.from(document.querySelectorAll(".tile"));
    if (btn.type === "id") {
        projectTiles.sort(function (a, b) {
            if (btn.reversed) {
                return b.pk - a.pk;
            }
            else {
                return a.pk - b.pk;
            }
        });
    }
    else if (btn.type === "name") {
        projectTiles.sort(function (a, b) {
            if (btn.reversed) {
                return a.name.localeCompare(b.name);
            }
            else {
                return b.name.localeCompare(a.name);
            }
        });
    }
    else if (btn.type === "phase") {
        projectTiles.sort(function (a, b) {
            if (btn.reversed) {
                return PhaseOrder[a.phase] - PhaseOrder[b.phase];
            }
            else {
                return PhaseOrder[a.phase] - PhaseOrder[b.phase];
            }
        });
    }
    else {
        throw new Error("Unkown Button type.");
    }
    if (tileContainer) {
        tileContainer.innerHTML = "";
        for (const tile of projectTiles) {
            tileContainer.appendChild(tile);
        }
    }
    console.log("sorting");
}
class SystoriSortButton extends HTMLButtonElement {
    constructor() {
        super();
        this.addEventListener("click", e => this.clickHandler(e));
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
    toggleReversed() {
        this.reversed = !this.reversed;
    }
    get active() {
        return this.classList.contains("active");
    }
    set active(active) {
        active ? this.classList.add("active") : this.classList.remove("active");
    }
    clickHandler(e) {
        this.toggleReversed();
        sortProjectTiles(e);
    }
}
customElements.define("sys-sort-button", SystoriSortButton, {
    extends: "button",
});
customElements.define("sys-project-tile", SystoriProjectTile, {
    extends: "div",
});
if (filterBar) {
    filterBar.classList.remove("hidden");
}
if (tileContainer) {
    tileContainer.classList.remove("hidden");
}


/***/ })

/******/ });
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8vd2VicGFjay9ib290c3RyYXAiLCJ3ZWJwYWNrOi8vLy4vc3JjL3Byb2plY3RfbGlzdC50cyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiO1FBQUE7UUFDQTs7UUFFQTtRQUNBOztRQUVBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBOztRQUVBO1FBQ0E7O1FBRUE7UUFDQTs7UUFFQTtRQUNBO1FBQ0E7OztRQUdBO1FBQ0E7O1FBRUE7UUFDQTs7UUFFQTtRQUNBO1FBQ0E7UUFDQSwwQ0FBMEMsZ0NBQWdDO1FBQzFFO1FBQ0E7O1FBRUE7UUFDQTtRQUNBO1FBQ0Esd0RBQXdELGtCQUFrQjtRQUMxRTtRQUNBLGlEQUFpRCxjQUFjO1FBQy9EOztRQUVBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQSx5Q0FBeUMsaUNBQWlDO1FBQzFFLGdIQUFnSCxtQkFBbUIsRUFBRTtRQUNySTtRQUNBOztRQUVBO1FBQ0E7UUFDQTtRQUNBLDJCQUEyQiwwQkFBMEIsRUFBRTtRQUN2RCxpQ0FBaUMsZUFBZTtRQUNoRDtRQUNBO1FBQ0E7O1FBRUE7UUFDQSxzREFBc0QsK0RBQStEOztRQUVySDtRQUNBOzs7UUFHQTtRQUNBOzs7Ozs7Ozs7Ozs7OztBQ2xGQSxNQUFNLFNBQVMsR0FBRyxRQUFRLENBQUMsYUFBYSxDQUFDLGFBQWEsQ0FBQyxDQUFDO0FBQ3hELE1BQU0sYUFBYSxHQUFHLFFBQVEsQ0FBQyxhQUFhLENBQUMsaUJBQWlCLENBQUMsQ0FBQztBQUNoRSxJQUFLLFVBUUo7QUFSRCxXQUFLLFVBQVU7SUFDWCx5REFBVztJQUNYLHFEQUFTO0lBQ1QsbURBQVE7SUFDUixxREFBUztJQUNULHVEQUFVO0lBQ1YsbURBQVE7SUFDUixtREFBUTtBQUNaLENBQUMsRUFSSSxVQUFVLEtBQVYsVUFBVSxRQVFkO0FBRUQsTUFBTSxrQkFBbUIsU0FBUSxjQUFjO0lBQzNDO1FBQ0ks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QUMsTUFBTSxDQUFDLGlCQUFpQixFQUFFLGlCQUFpQixFQUFFO0lBQ3hELE9BQU8sRUFBRSxRQUFRO0NBQ3BCLENBQUMsQ0FBQztBQUNILGNBQWMsQ0FBQyxNQUFNLENBQUMsa0JBQWtCLEVBQUUsa0JBQWtCLEVBQUU7SUFDMUQsT0FBTyxFQUFFLEtBQUs7Q0FDakIsQ0FBQyxDQUFDO0FBRUgsSUFBSSxTQUFTLEVBQUU7SUFDWCxTQUFTLENBQUMsU0FBUyxDQUFDLE1BQU0sQ0FBQyxRQUFRLENBQUMsQ0FBQztDQUN4QztBQUNELElBQUksYUFBYSxFQUFFO0lBQ2YsYUFBYSxDQUFDLFNBQVMsQ0FBQyxNQUFNLENBQUMsUUFBUSxDQUFDLENBQUM7Q0FDNUMiLCJmaWxlIjoicHJvamVjdF9saXN0LmpzIiwic291cmNlc0NvbnRlbnQiOlsiIFx0Ly8gVGhlIG1vZHVsZSBjYWNoZVxuIFx0dmFyIGluc3RhbGxlZE1vZHVsZXMgPSB7fTtcblxuIFx0Ly8gVGhlIHJlcXVpcmUgZnVuY3Rpb25cbiBcdGZ1bmN0aW9uIF9fd2VicGFja19yZXF1aXJlX18obW9kdWxlSWQpIHtcblxuIFx0XHQvLyBDaGVjayBpZiBtb2R1bGUgaXMgaW4gY2FjaGVcbiBcdFx0aWYoaW5zdGFsbGVkTW9kdWxlc1ttb2R1bGVJZF0pIHtcbiBcdFx0XHRyZXR1cm4gaW5zdGFsbGVkTW9kdWxlc1ttb2R1bGVJZF0uZXhwb3J0cztcbiBcdFx0fVxuIFx0XHQvLyBDcmVhdGUgYSBuZXcgbW9kdWxlIChhbmQgcHV0IGl0IGludG8gdGhlIGNhY2hlKVxuIFx0XHR2YXIgbW9kdWxlID0gaW5zdGFsbGVkTW9kdWxlc1ttb2R1bGVJZF0gPSB7XG4gXHRcdFx0aTogbW9kdWxlSWQsXG4gXHRcdFx0bDogZmFsc2UsXG4gXHRcdFx0ZXhwb3J0czoge31cbiBcdFx0fTtcblxuIFx0XHQvLyBFeGVjdXRlIHRoZSBtb2R1bGUgZnVuY3Rpb25cbiBcdFx0bW9kdWxlc1ttb2R1bGVJZF0uY2FsbChtb2R1bGUuZXhwb3J0cywgbW9kdWxlLCBtb2R1bGUuZXhwb3J0cywgX193ZWJwYWNrX3JlcXVpcmVfXyk7XG5cbiBcdFx0Ly8gRmxhZyB0aGUgbW9kdWxlIGFzIGxvYWRlZFxuIFx0XHRtb2R1bGUubCA9IHRydWU7XG5cbiBcdFx0Ly8gUmV0dXJuIHRoZSBleHBvcnRzIG9mIHRoZSBtb2R1bGVcbiBcdFx0cmV0dXJuIG1vZHVsZS5leHBvcnRzO1xuIFx0fVxuXG5cbiBcdC8vIGV4cG9zZSB0aGUgbW9kdWxlcyBvYmplY3QgKF9fd2VicGFja19tb2R1bGVzX18pXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLm0gPSBtb2R1bGVzO1xuXG4gXHQvLyBleHBvc2UgdGhlIG1vZHVsZSBjYWNoZVxuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy5jID0gaW5zdGFsbGVkTW9kdWxlcztcblxuIFx0Ly8gZGVmaW5lIGdldHRlciBmdW5jdGlvbiBmb3IgaGFybW9ueSBleHBvcnRzXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLmQgPSBmdW5jdGlvbihleHBvcnRzLCBuYW1lLCBnZXR0ZXIpIHtcbiBcdFx0aWYoIV9fd2VicGFja19yZXF1aXJlX18ubyhleHBvcnRzLCBuYW1lKSkge1xuIFx0XHRcdE9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBuYW1lLCB7IGVudW1lcmFibGU6IHRydWUsIGdldDogZ2V0dGVyIH0pO1xuIFx0XHR9XG4gXHR9O1xuXG4gXHQvLyBkZWZpbmUgX19lc01vZHVsZSBvbiBleHBvcnRzXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLnIgPSBmdW5jdGlvbihleHBvcnRzKSB7XG4gXHRcdGlmKHR5cGVvZiBTeW1ib2wgIT09ICd1bmRlZmluZWQnICYmIFN5bWJvbC50b1N0cmluZ1RhZykge1xuIFx0XHRcdE9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBTeW1ib2wudG9TdHJpbmdUYWcsIHsgdmFsdWU6ICdNb2R1bGUnIH0pO1xuIFx0XHR9XG4gXHRcdE9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCAnX19lc01vZHVsZScsIHsgdmFsdWU6IHRydWUgfSk7XG4gXHR9O1xuXG4gXHQvLyBjcmVhdGUgYSBmYWtlIG5hbWVzcGFjZSBvYmplY3RcbiBcdC8vIG1vZGUgJiAxOiB2YWx1ZSBpcyBhIG1vZHVsZSBpZCwgcmVxdWlyZSBpdFxuIFx0Ly8gbW9kZSAmIDI6IG1lcmdlIGFsbCBwcm9wZXJ0aWVzIG9mIHZhbHVlIGludG8gdGhlIG5zXG4gXHQvLyBtb2RlICYgNDogcmV0dXJuIHZhbHVlIHdoZW4gYWxyZWFkeSBucyBvYmplY3RcbiBcdC8vIG1vZGUgJiA4fDE6IGJlaGF2ZSBsaWtlIHJlcXVpcmVcbiBcdF9fd2VicGFja19yZXF1aXJlX18udCA9IGZ1bmN0aW9uKHZhbHVlLCBtb2RlKSB7XG4gXHRcdGlmKG1vZGUgJiAxKSB2YWx1ZSA9IF9fd2VicGFja19yZXF1aXJlX18odmFsdWUpO1xuIFx0XHRpZihtb2RlICYgOCkgcmV0dXJuIHZhbHVlO1xuIFx0XHRpZigobW9kZSAmIDQpICYmIHR5cGVvZiB2YWx1ZSA9PT0gJ29iamVjdCcgJiYgdmFsdWUgJiYgdmFsdWUuX19lc01vZHVsZSkgcmV0dXJuIHZhbHVlO1xuIFx0XHR2YXIgbnMgPSBPYmplY3QuY3JlYXRlKG51bGwpO1xuIFx0XHRfX3dlYnBhY2tfcmVxdWlyZV9fLnIobnMpO1xuIFx0XHRPYmplY3QuZGVmaW5lUHJvcGVydHkobnMsICdkZWZhdWx0JywgeyBlbnVtZXJhYmxlOiB0cnVlLCB2YWx1ZTogdmFsdWUgfSk7XG4gXHRcdGlmKG1vZGUgJiAyICYmIHR5cGVvZiB2YWx1ZSAhPSAnc3RyaW5nJykgZm9yKHZhciBrZXkgaW4gdmFsdWUpIF9fd2VicGFja19yZXF1aXJlX18uZChucywga2V5LCBmdW5jdGlvbihrZXkpIHsgcmV0dXJuIHZhbHVlW2tleV07IH0uYmluZChudWxsLCBrZXkpKTtcbiBcdFx0cmV0dXJuIG5zO1xuIFx0fTtcblxuIFx0Ly8gZ2V0RGVmYXVsdEV4cG9ydCBmdW5jdGlvbiBmb3IgY29tcGF0aWJpbGl0eSB3aXRoIG5vbi1oYXJtb255IG1vZHVsZXNcbiBcdF9fd2VicGFja19yZXF1aXJlX18ubiA9IGZ1bmN0aW9uKG1vZHVsZSkge1xuIFx0XHR2YXIgZ2V0dGVyID0gbW9kdWxlICYmIG1vZHVsZS5fX2VzTW9kdWxlID9cbiBcdFx0XHRmdW5jdGlvbiBnZXREZWZhdWx0KCkgeyByZXR1cm4gbW9kdWxlWydkZWZhdWx0J107IH0gOlxuIFx0XHRcdGZ1bmN0aW9uIGdldE1vZHVsZUV4cG9ydHMoKSB7IHJldHVybiBtb2R1bGU7IH07XG4gXHRcdF9fd2VicGFja19yZXF1aXJlX18uZChnZXR0ZXIsICdhJywgZ2V0dGVyKTtcbiBcdFx0cmV0dXJuIGdldHRlcjtcbiBcdH07XG5cbiBcdC8vIE9iamVjdC5wcm90b3R5cGUuaGFzT3duUHJvcGVydHkuY2FsbFxuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy5vID0gZnVuY3Rpb24ob2JqZWN0LCBwcm9wZXJ0eSkgeyByZXR1cm4gT2JqZWN0LnByb3RvdHlwZS5oYXNPd25Qcm9wZXJ0eS5jYWxsKG9iamVjdCwgcHJvcGVydHkpOyB9O1xuXG4gXHQvLyBfX3dlYnBhY2tfcHVibGljX3BhdGhfX1xuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy5wID0gXCJcIjtcblxuXG4gXHQvLyBMb2FkIGVudHJ5IG1vZHVsZSBhbmQgcmV0dXJuIGV4cG9ydHNcbiBcdHJldHVybiBfX3dlYnBhY2tfcmVxdWlyZV9fKF9fd2VicGFja19yZXF1aXJlX18ucyA9IFwiLi9zcmMvcHJvamVjdF9saXN0LnRzXCIpO1xuIiwiY29uc3QgZmlsdGVyQmFyID0gZG9jdW1lbnQucXVlcnlTZWxlY3RvcihcIiNmaWx0ZXItYmFyXCIpO1xuY29uc3QgdGlsZUNvbnRhaW5lciA9IGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3IoXCIjdGlsZS1jb250YWluZXJcIik7XG5lbnVtIFBoYXNlT3JkZXIge1xuICAgIHByb3NwZWN0aXZlLFxuICAgIHRlbmRlcmluZyxcbiAgICBwbGFubmluZyxcbiAgICBleGVjdXRpbmcsXG4gICAgc2V0dGxlbWVudCxcbiAgICB3YXJyYW50eSxcbiAgICBmaW5pc2hlZCxcbn1cblxuY2xhc3MgU3lzdG9yaVByb2plY3RUaWxlIGV4dGVuZHMgSFRNTERpdkVsZW1lbnQge1xuICAgIGNvbnN0cnVjdG9yKCkge1xuICAgICAgICBzdXBlcigpO1xuICAgIH1cbiAgICBnZXQgcGsoKTogbnVtYmVyIHtcbiAgICAgICAgcmV0dXJuIE51bWJlcih0aGlzLmRhdGFzZXRbXCJwa1wiXSB8fCBcIjBcIik7XG4gICAgfVxuICAgIGdldCBuYW1lKCk6IHN0cmluZyB7XG4gICAgICAgIHJldHVybiB0aGlzLmRhdGFzZXRbXCJuYW1lXCJdIHx8IFwidW5rbm93blwiO1xuICAgIH1cbiAgICBnZXQgcGhhc2UoKTogUGhhc2VPcmRlciB7XG4gICAgICAgIHJldHVybiAodGhpcy5kYXRhc2V0W1wicGhhc2VcIl0gfHwgUGhhc2VPcmRlci5wcm9zcGVjdGl2ZSkgYXMgUGhhc2VPcmRlcjtcbiAgICB9XG59XG5cbmZ1bmN0aW9uIHNvcnRQcm9qZWN0VGlsZXMoZTogRXZlbnQpOiB2b2lkIHtcbiAgICBjb25zdCBidG4gPSBlLnRhcmdldCBhcyBTeXN0b3JpU29ydEJ1dHRvbjtcbiAgICBpZiAoIWJ0bilcbiAgICAgICAgdGhyb3cgbmV3IEVycm9yKFxuICAgICAgICAgICAgYEV4cGVjdGVkIFN5c3RvcmlTb3J0QnV0dG9uIGFzIEV2ZW50VGFyZ2V0IGJ1dCBnb3QgJHtlLnRhcmdldH0uYCxcbiAgICAgICAgKTtcbiAgICBjb25zdCBwcm9qZWN0VGlsZXMgPSBBcnJheS5mcm9tKFxuICAgICAgICBkb2N1bWVudC5xdWVyeVNlbGVjdG9yQWxsPFN5c3RvcmlQcm9qZWN0VGlsZT4oXCIudGlsZVwiKSxcbiAgICApO1xuXG4gICAgaWYgKGJ0bi50eXBlID09PSBcImlkXCIpIHtcbiAgICAgICAgcHJvamVjdFRpbGVzLnNvcnQoZnVuY3Rpb24oXG4gICAgICAgICAgICBhOiBTeXN0b3JpUHJvamVjdFRpbGUsXG4gICAgICAgICAgICBiOiBTeXN0b3JpUHJvamVjdFRpbGUsXG4gICAgICAgICkge1xuICAgICAgICAgICAgaWYgKGJ0bi5yZXZlcnNlZCkge1xuICAgICAgICAgICAgICAgIHJldHVybiBiLnBrIC0gYS5waztcbiAgICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICAgICAgcmV0dXJuIGEucGsgLSBiLnBrO1xuICAgICAgICAgICAgfVxuICAgICAgICB9KTtcbiAgICB9IGVsc2UgaWYgKGJ0bi50eXBlID09PSBcIm5hbWVcIikge1xuICAgICAgICBwcm9qZWN0VGlsZXMuc29ydChmdW5jdGlvbihcbiAgICAgICAgICAgIGE6IFN5c3RvcmlQcm9qZWN0VGlsZSxcbiAgICAgICAgICAgIGI6IFN5c3RvcmlQcm9qZWN0VGlsZSxcbiAgICAgICAgKSB7XG4gICAgICAgICAgICBpZiAoYnRuLnJldmVyc2VkKSB7XG4gICAgICAgICAgICAgICAgcmV0dXJuIGEubmFtZS5sb2NhbGVDb21wYXJlKGIubmFtZSk7XG4gICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgIHJldHVybiBiLm5hbWUubG9jYWxlQ29tcGFyZShhLm5hbWUpO1xuICAgICAgICAgICAgfVxuICAgICAgICB9KTtcbiAgICB9IGVsc2UgaWYgKGJ0bi50eXBlID09PSBcInBoYXNlXCIpIHtcbiAgICAgICAgcHJvamVjdFRpbGVzLnNvcnQoZnVuY3Rpb24oXG4gICAgICAgICAgICBhOiBTeXN0b3JpUHJvamVjdFRpbGUsXG4gICAgICAgICAgICBiOiBTeXN0b3JpUHJvamVjdFRpbGUsXG4gICAgICAgICkge1xuICAgICAgICAgICAgaWYgKGJ0bi5yZXZlcnNlZCkge1xuICAgICAgICAgICAgICAgIHJldHVybiBQaGFzZU9yZGVyW2EucGhhc2VdIC0gUGhhc2VPcmRlcltiLnBoYXNlXTtcbiAgICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICAgICAgcmV0dXJuIFBoYXNlT3JkZXJbYS5waGFzZV0gLSBQaGFzZU9yZGVyW2IucGhhc2VdO1xuICAgICAgICAgICAgfVxuICAgICAgICB9KTtcbiAgICB9IGVsc2Uge1xuICAgICAgICB0aHJvdyBuZXcgRXJyb3IoXCJVbmtvd24gQnV0dG9uIHR5cGUuXCIpO1xuICAgIH1cblxuICAgIGlmICh0aWxlQ29udGFpbmVyKSB7XG4gICAgICAgIHRpbGVDb250YWluZXIuaW5uZXJIVE1MID0gXCJcIjtcbiAgICAgICAgZm9yIChjb25zdCB0aWxlIG9mIHByb2plY3RUaWxlcykge1xuICAgICAgICAgICAgdGlsZUNvbnRhaW5lci5hcHBlbmRDaGlsZCh0aWxlKTtcbiAgICAgICAgfVxuICAgIH1cbiAgICBjb25zb2xlLmxvZyhcInNvcnRpbmdcIik7XG59XG5cbmNsYXNzIFN5c3RvcmlTb3J0QnV0dG9uIGV4dGVuZHMgSFRNTEJ1dHRvbkVsZW1lbnQge1xuICAgIGNvbnN0cnVjdG9yKCkge1xuICAgICAgICBzdXBlcigpO1xuICAgICAgICB0aGlzLmFkZEV2ZW50TGlzdGVuZXIoXCJjbGlja1wiLCBlID0+IHRoaXMuY2xpY2tIYW5kbGVyKGUpKTtcbiAgICB9XG4gICAgZ2V0IHR5cGUoKTogc3RyaW5nIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuZGF0YXNldFtcInR5cGVcIl0gfHwgXCJcIjtcbiAgICB9XG4gICAgc2V0IHR5cGUodHlwZTogc3RyaW5nKSB7XG4gICAgICAgIHRoaXMuZGF0YXNldFtcInR5cGVcIl0gPSB0eXBlO1xuICAgIH1cblxuICAgIGdldCByZXZlcnNlZCgpOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuZGF0YXNldFtcInJldmVyc2VkXCJdID09IFwidHJ1ZVwiO1xuICAgIH1cbiAgICBzZXQgcmV2ZXJzZWQocmV2ZXJzZWQ6IGJvb2xlYW4pIHtcbiAgICAgICAgcmV2ZXJzZWRcbiAgICAgICAgICAgID8gKHRoaXMuZGF0YXNldFtcInJldmVyc2VkXCJdID0gXCJ0cnVlXCIpXG4gICAgICAgICAgICA6ICh0aGlzLmRhdGFzZXRbXCJyZXZlcnNlZFwiXSA9IFwiZmFsc2VcIik7XG4gICAgfVxuICAgIHRvZ2dsZVJldmVyc2VkKCk6IHZvaWQge1xuICAgICAgICB0aGlzLnJldmVyc2VkID0gIXRoaXMucmV2ZXJzZWQ7XG4gICAgfVxuXG4gICAgZ2V0IGFjdGl2ZSgpOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuY2xhc3NMaXN0LmNvbnRhaW5zKFwiYWN0aXZlXCIpO1xuICAgIH1cbiAgICBzZXQgYWN0aXZlKGFjdGl2ZTogYm9vbGVhbikge1xuICAgICAgICBhY3RpdmUgPyB0aGlzLmNsYXNzTGlzdC5hZGQoXCJhY3RpdmVcIikgOiB0aGlzLmNsYXNzTGlzdC5yZW1vdmUoXCJhY3RpdmVcIik7XG4gICAgfVxuICAgIGNsaWNrSGFuZGxlcihlOiBFdmVudCk6IHZvaWQge1xuICAgICAgICB0aGlzLnRvZ2dsZVJldmVyc2VkKCk7XG4gICAgICAgIHNvcnRQcm9qZWN0VGlsZXMoZSk7XG4gICAgfVxufVxuXG5jdXN0b21FbGVtZW50cy5kZWZpbmUoXCJzeXMtc29ydC1idXR0b25cIiwgU3lzdG9yaVNvcnRCdXR0b24sIHtcbiAgICBleHRlbmRzOiBcImJ1dHRvblwiLFxufSk7XG5jdXN0b21FbGVtZW50cy5kZWZpbmUoXCJzeXMtcHJvamVjdC10aWxlXCIsIFN5c3RvcmlQcm9qZWN0VGlsZSwge1xuICAgIGV4dGVuZHM6IFwiZGl2XCIsXG59KTtcblxuaWYgKGZpbHRlckJhcikge1xuICAgIGZpbHRlckJhci5jbGFzc0xpc3QucmVtb3ZlKFwiaGlkZGVuXCIpO1xufVxuaWYgKHRpbGVDb250YWluZXIpIHtcbiAgICB0aWxlQ29udGFpbmVyLmNsYXNzTGlzdC5yZW1vdmUoXCJoaWRkZW5cIik7XG59XG4iXSwic291cmNlUm9vdCI6IiJ9