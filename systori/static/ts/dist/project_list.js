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
        return parseInt(this.dataset["pk"]);
    }
    get name() {
        return this.dataset["name"];
    }
    get phase() {
        return (this.dataset["phase"] || PhaseOrder.prospective);
    }
    get hidden() {
        return this.classList.contains("hidden") === true;
    }
    hide(hide) {
        hide ? this.classList.add("hidden") : this.classList.remove("hidden");
    }
}
class SystoriSortButton extends HTMLElement {
    constructor() {
        super();
        this.addEventListener("click", () => this.sortProjectTiles(true));
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
    // ASC/DESC sorting order
    get asc() {
        return this.dataset["asc"] == "true";
    }
    set asc(asc) {
        asc ? (this.dataset["asc"] = "true") : (this.dataset["asc"] = "false");
    }
    toggleAsc() {
        this.asc = !this.asc;
    }
    get active() {
        return this.classList.contains("active");
    }
    set active(status) {
        status ? this.classList.add("active") : this.classList.remove("active");
    }
    // adds class `active` to active button and removes it from all others.
    activateExclusive() {
        const btns = Array.from(document.querySelectorAll("sys-sort-button"));
        for (const btn of btns) {
            btn.active = false;
        }
        this.active = true;
    }
    sortProjectTiles(toggleAsc) {
        // starting with toggling sorting order, move to bottom to exchange true/false behaviour
        if (toggleAsc)
            this.toggleAsc();
        this.activateExclusive();
        const projectTiles = Array.from(document.querySelectorAll(".tile"));
        projectTiles.sort((a, b) => {
            switch (this.type) {
                case SortButtonType.id:
                    if (this.asc) {
                        return b.pk < a.pk ? -1 : 1;
                    }
                    else {
                        return a.pk < b.pk ? -1 : 1;
                    }
                case SortButtonType.name:
                    if (this.asc) {
                        return a.name.localeCompare(b.name);
                    }
                    else {
                        return b.name.localeCompare(a.name);
                    }
                case SortButtonType.phase:
                    if (this.asc) {
                        return PhaseOrder[b.phase] <= PhaseOrder[a.phase]
                            ? -1
                            : 1;
                    }
                    else {
                        return PhaseOrder[a.phase] <= PhaseOrder[b.phase]
                            ? -1
                            : 1;
                    }
                default:
                    throw new Error(`Can't find a SortButtonType type for ${this.type}.`);
            }
        });
        if (tileContainer) {
            tileContainer.innerHTML = "";
            for (const tile of projectTiles) {
                tileContainer.appendChild(tile);
            }
        }
        this.saveStateToLocalStorage();
    }
    saveStateToLocalStorage() {
        localStorage.setItem("state-SystoriSortButton", JSON.stringify({
            type: this.type,
            asc: this.asc,
        }));
    }
}
function savePhaseStateToLocalStorage() {
    const btns = Array.from(document.querySelectorAll("sys-phase-button"));
    const btnsState = [];
    for (const btn of btns) {
        btnsState.push({ phase: btn.phase, hidePhase: btn.hidePhase });
    }
    localStorage.setItem("state-SystoriPhaseButton", JSON.stringify(btnsState));
}
class SystoriPhaseButton extends HTMLElement {
    constructor() {
        super();
        this.addEventListener("click", () => this.filterProjectTiles(true));
    }
    get phase() {
        return this.dataset["phase"];
    }
    set phase(phase) {
        this.dataset["phase"] = phase;
    }
    // hidePhase === hidden
    get hidePhase() {
        return this.classList.contains("hide-phase");
    }
    set hidePhase(hide) {
        hide
            ? this.classList.add("hide-phase")
            : this.classList.remove("hide-phase");
    }
    toggleProjectTiles(hide) {
        const projectTiles = Array.from(document.querySelectorAll(`sys-project-tile[data-phase=${this.phase}]`));
        for (const tile of projectTiles) {
            tile.hide(hide);
        }
        savePhaseStateToLocalStorage();
    }
    filterProjectTiles(toggle) {
        if (toggle)
            this.hidePhase = !this.hidePhase;
        this.hidePhase
            ? this.toggleProjectTiles(true)
            : this.toggleProjectTiles(false);
    }
}
class SystoriSearchElement extends HTMLElement {
    // This custom element is for composing the two childNodes.
    constructor() {
        super();
    }
}
class SystoriSearchInput extends HTMLInputElement {
    constructor() {
        super();
        this.addEventListener("keyup", () => this.apiSearchProjects());
    }
    apiSearchProjects() {
        const projects = [];
        projects.push(11);
        projects.push(23);
        return projects;
    }
}
function loadLocalStorage() {
    const sortJson = localStorage.getItem("state-SystoriSortButton");
    const phaseJson = localStorage.getItem("state-SystoriPhaseButton");
    if (sortJson) {
        const state = JSON.parse(sortJson);
        const btns = Array.from(document.querySelectorAll("sys-sort-button"));
        for (const btn of btns) {
            if (btn.type === state.type) {
                console.log(`loading from localStorage for ${btn.type}.`);
                btn.asc = state.asc;
                btn.sortProjectTiles(false);
            }
            else {
                btn.active = false;
            }
        }
    }
    if (phaseJson) {
        const state = JSON.parse(phaseJson);
        const btns = Array.from(document.querySelectorAll("sys-phase-button"));
        for (const p of state) {
            if (p.hidePhase) {
                for (const btn of btns) {
                    if (btn.phase === p.phase) {
                        btn.hidePhase = p.hidePhase;
                        btn.filterProjectTiles(false);
                    }
                }
            }
        }
    }
}
customElements.define("sys-search-input", SystoriSearchInput, {
    extends: "input",
});
customElements.define("sys-search-element", SystoriSearchElement);
customElements.define("sys-phase-button", SystoriPhaseButton);
customElements.define("sys-sort-button", SystoriSortButton);
customElements.define("sys-project-tile", SystoriProjectTile);
loadLocalStorage();
if (filterBar) {
    filterBar.classList.remove("hidden");
}
if (tileContainer) {
    tileContainer.classList.remove("hidden");
}


/***/ })

/******/ });
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8vd2VicGFjay9ib290c3RyYXAiLCJ3ZWJwYWNrOi8vLy4vc3JjL3Byb2plY3RfbGlzdC50cyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiO1FBQUE7UUFDQTs7UUFFQTtRQUNBOztRQUVBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBOztRQUVBO1FBQ0E7O1FBRUE7UUFDQTs7UUFFQTtRQUNBO1FBQ0E7OztRQUdBO1FBQ0E7O1FBRUE7UUFDQTs7UUFFQTtRQUNBO1FBQ0E7UUFDQSwwQ0FBMEMsZ0NBQWdDO1FBQzFFO1FBQ0E7O1FBRUE7UUFDQTtRQUNBO1FBQ0Esd0RBQXdELGtCQUFrQjtRQUMxRTtRQUNBLGlEQUFpRCxjQUFjO1FBQy9EOztRQUVBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQSx5Q0FBeUMsaUNBQWlDO1FBQzFFLGdIQUFnSCxtQkFBbUIsRUFBRTtRQUNySTtRQUNBOztRQUVBO1FBQ0E7UUFDQTtRQUNBLDJCQUEyQiwwQkFBMEIsRUFBRTtRQUN2RCxpQ0FBaUMsZUFBZTtRQUNoRDtRQUNBO1FBQ0E7O1FBRUE7UUFDQSxzREFBc0QsK0RBQStEOztRQUVySDtRQUNBOzs7UUFHQTtRQUNBOzs7Ozs7Ozs7Ozs7OztBQ2xGQSxNQUFNLFNBQVMsR0FBRyxRQUFRLENBQUMsYUFBYSxDQUFDLGFBQWEsQ0FBQyxDQUFDO0FBQ3hELE1BQU0sYUFBYSxHQUFHLFFBQVEsQ0FBQyxhQUFhLENBQUMsaUJBQWlCLENBQUMsQ0FBQztBQUNoRSxJQUFLLFVBUUo7QUFSRCxXQUFLLFVBQVU7SUFDWCx5REFBVztJQUNYLHFEQUFTO0lBQ1QsbURBQVE7SUFDUixxREFBUztJQUNULHVEQUFVO0lBQ1YsbURBQVE7SUFDUixtREFBUTtBQUNaLENBQUMsRUFSSSxVQUFVLEtBQVYsVUFBVSxRQVFkO0FBQ0QsSUFBSyxjQUlKO0FBSkQsV0FBSyxjQUFjO0lBQ2YsMkJB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QUFDO3dCQUM1QixHQUFHLENBQUMsa0JBQWtCLENBQUMsS0FBSyxDQUFDLENBQUM7cUJBQ2pDO2lCQUNKO2FBQ0o7U0FDSjtLQUNKO0FBQ0wsQ0FBQztBQUVELGNBQWMsQ0FBQyxNQUFNLENBQUMsa0JBQWtCLEVBQUUsa0JBQWtCLEVBQUU7SUFDMUQsT0FBTyxFQUFFLE9BQU87Q0FDbkIsQ0FBQyxDQUFDO0FBQ0gsY0FBYyxDQUFDLE1BQU0sQ0FBQyxvQkFBb0IsRUFBRSxvQkFBb0IsQ0FBQyxDQUFDO0FBQ2xFLGNBQWMsQ0FBQyxNQUFNLENBQUMsa0JBQWtCLEVBQUUsa0JBQWtCLENBQUMsQ0FBQztBQUM5RCxjQUFjLENBQUMsTUFBTSxDQUFDLGlCQUFpQixFQUFFLGlCQUFpQixDQUFDLENBQUM7QUFDNUQsY0FBYyxDQUFDLE1BQU0sQ0FBQyxrQkFBa0IsRUFBRSxrQkFBa0IsQ0FBQyxDQUFDO0FBRTlELGdCQUFnQixFQUFFLENBQUM7QUFDbkIsSUFBSSxTQUFTLEVBQUU7SUFDWCxTQUFTLENBQUMsU0FBUyxDQUFDLE1BQU0sQ0FBQyxRQUFRLENBQUMsQ0FBQztDQUN4QztBQUNELElBQUksYUFBYSxFQUFFO0lBQ2YsYUFBYSxDQUFDLFNBQVMsQ0FBQyxNQUFNLENBQUMsUUFBUSxDQUFDLENBQUM7Q0FDNUMiLCJmaWxlIjoicHJvamVjdF9saXN0LmpzIiwic291cmNlc0NvbnRlbnQiOlsiIFx0Ly8gVGhlIG1vZHVsZSBjYWNoZVxuIFx0dmFyIGluc3RhbGxlZE1vZHVsZXMgPSB7fTtcblxuIFx0Ly8gVGhlIHJlcXVpcmUgZnVuY3Rpb25cbiBcdGZ1bmN0aW9uIF9fd2VicGFja19yZXF1aXJlX18obW9kdWxlSWQpIHtcblxuIFx0XHQvLyBDaGVjayBpZiBtb2R1bGUgaXMgaW4gY2FjaGVcbiBcdFx0aWYoaW5zdGFsbGVkTW9kdWxlc1ttb2R1bGVJZF0pIHtcbiBcdFx0XHRyZXR1cm4gaW5zdGFsbGVkTW9kdWxlc1ttb2R1bGVJZF0uZXhwb3J0cztcbiBcdFx0fVxuIFx0XHQvLyBDcmVhdGUgYSBuZXcgbW9kdWxlIChhbmQgcHV0IGl0IGludG8gdGhlIGNhY2hlKVxuIFx0XHR2YXIgbW9kdWxlID0gaW5zdGFsbGVkTW9kdWxlc1ttb2R1bGVJZF0gPSB7XG4gXHRcdFx0aTogbW9kdWxlSWQsXG4gXHRcdFx0bDogZmFsc2UsXG4gXHRcdFx0ZXhwb3J0czoge31cbiBcdFx0fTtcblxuIFx0XHQvLyBFeGVjdXRlIHRoZSBtb2R1bGUgZnVuY3Rpb25cbiBcdFx0bW9kdWxlc1ttb2R1bGVJZF0uY2FsbChtb2R1bGUuZXhwb3J0cywgbW9kdWxlLCBtb2R1bGUuZXhwb3J0cywgX193ZWJwYWNrX3JlcXVpcmVfXyk7XG5cbiBcdFx0Ly8gRmxhZyB0aGUgbW9kdWxlIGFzIGxvYWRlZFxuIFx0XHRtb2R1bGUubCA9IHRydWU7XG5cbiBcdFx0Ly8gUmV0dXJuIHRoZSBleHBvcnRzIG9mIHRoZSBtb2R1bGVcbiBcdFx0cmV0dXJuIG1vZHVsZS5leHBvcnRzO1xuIFx0fVxuXG5cbiBcdC8vIGV4cG9zZSB0aGUgbW9kdWxlcyBvYmplY3QgKF9fd2VicGFja19tb2R1bGVzX18pXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLm0gPSBtb2R1bGVzO1xuXG4gXHQvLyBleHBvc2UgdGhlIG1vZHVsZSBjYWNoZVxuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy5jID0gaW5zdGFsbGVkTW9kdWxlcztcblxuIFx0Ly8gZGVmaW5lIGdldHRlciBmdW5jdGlvbiBmb3IgaGFybW9ueSBleHBvcnRzXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLmQgPSBmdW5jdGlvbihleHBvcnRzLCBuYW1lLCBnZXR0ZXIpIHtcbiBcdFx0aWYoIV9fd2VicGFja19yZXF1aXJlX18ubyhleHBvcnRzLCBuYW1lKSkge1xuIFx0XHRcdE9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBuYW1lLCB7IGVudW1lcmFibGU6IHRydWUsIGdldDogZ2V0dGVyIH0pO1xuIFx0XHR9XG4gXHR9O1xuXG4gXHQvLyBkZWZpbmUgX19lc01vZHVsZSBvbiBleHBvcnRzXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLnIgPSBmdW5jdGlvbihleHBvcnRzKSB7XG4gXHRcdGlmKHR5cGVvZiBTeW1ib2wgIT09ICd1bmRlZmluZWQnICYmIFN5bWJvbC50b1N0cmluZ1RhZykge1xuIFx0XHRcdE9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBTeW1ib2wudG9TdHJpbmdUYWcsIHsgdmFsdWU6ICdNb2R1bGUnIH0pO1xuIFx0XHR9XG4gXHRcdE9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCAnX19lc01vZHVsZScsIHsgdmFsdWU6IHRydWUgfSk7XG4gXHR9O1xuXG4gXHQvLyBjcmVhdGUgYSBmYWtlIG5hbWVzcGFjZSBvYmplY3RcbiBcdC8vIG1vZGUgJiAxOiB2YWx1ZSBpcyBhIG1vZHVsZSBpZCwgcmVxdWlyZSBpdFxuIFx0Ly8gbW9kZSAmIDI6IG1lcmdlIGFsbCBwcm9wZXJ0aWVzIG9mIHZhbHVlIGludG8gdGhlIG5zXG4gXHQvLyBtb2RlICYgNDogcmV0dXJuIHZhbHVlIHdoZW4gYWxyZWFkeSBucyBvYmplY3RcbiBcdC8vIG1vZGUgJiA4fDE6IGJlaGF2ZSBsaWtlIHJlcXVpcmVcbiBcdF9fd2VicGFja19yZXF1aXJlX18udCA9IGZ1bmN0aW9uKHZhbHVlLCBtb2RlKSB7XG4gXHRcdGlmKG1vZGUgJiAxKSB2YWx1ZSA9IF9fd2VicGFja19yZXF1aXJlX18odmFsdWUpO1xuIFx0XHRpZihtb2RlICYgOCkgcmV0dXJuIHZhbHVlO1xuIFx0XHRpZigobW9kZSAmIDQpICYmIHR5cGVvZiB2YWx1ZSA9PT0gJ29iamVjdCcgJiYgdmFsdWUgJiYgdmFsdWUuX19lc01vZHVsZSkgcmV0dXJuIHZhbHVlO1xuIFx0XHR2YXIgbnMgPSBPYmplY3QuY3JlYXRlKG51bGwpO1xuIFx0XHRfX3dlYnBhY2tfcmVxdWlyZV9fLnIobnMpO1xuIFx0XHRPYmplY3QuZGVmaW5lUHJvcGVydHkobnMsICdkZWZhdWx0JywgeyBlbnVtZXJhYmxlOiB0cnVlLCB2YWx1ZTogdmFsdWUgfSk7XG4gXHRcdGlmKG1vZGUgJiAyICYmIHR5cGVvZiB2YWx1ZSAhPSAnc3RyaW5nJykgZm9yKHZhciBrZXkgaW4gdmFsdWUpIF9fd2VicGFja19yZXF1aXJlX18uZChucywga2V5LCBmdW5jdGlvbihrZXkpIHsgcmV0dXJuIHZhbHVlW2tleV07IH0uYmluZChudWxsLCBrZXkpKTtcbiBcdFx0cmV0dXJuIG5zO1xuIFx0fTtcblxuIFx0Ly8gZ2V0RGVmYXVsdEV4cG9ydCBmdW5jdGlvbiBmb3IgY29tcGF0aWJpbGl0eSB3aXRoIG5vbi1oYXJtb255IG1vZHVsZXNcbiBcdF9fd2VicGFja19yZXF1aXJlX18ubiA9IGZ1bmN0aW9uKG1vZHVsZSkge1xuIFx0XHR2YXIgZ2V0dGVyID0gbW9kdWxlICYmIG1vZHVsZS5fX2VzTW9kdWxlID9cbiBcdFx0XHRmdW5jdGlvbiBnZXREZWZhdWx0KCkgeyByZXR1cm4gbW9kdWxlWydkZWZhdWx0J107IH0gOlxuIFx0XHRcdGZ1bmN0aW9uIGdldE1vZHVsZUV4cG9ydHMoKSB7IHJldHVybiBtb2R1bGU7IH07XG4gXHRcdF9fd2VicGFja19yZXF1aXJlX18uZChnZXR0ZXIsICdhJywgZ2V0dGVyKTtcbiBcdFx0cmV0dXJuIGdldHRlcjtcbiBcdH07XG5cbiBcdC8vIE9iamVjdC5wcm90b3R5cGUuaGFzT3duUHJvcGVydHkuY2FsbFxuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy5vID0gZnVuY3Rpb24ob2JqZWN0LCBwcm9wZXJ0eSkgeyByZXR1cm4gT2JqZWN0LnByb3RvdHlwZS5oYXNPd25Qcm9wZXJ0eS5jYWxsKG9iamVjdCwgcHJvcGVydHkpOyB9O1xuXG4gXHQvLyBfX3dlYnBhY2tfcHVibGljX3BhdGhfX1xuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy5wID0gXCJcIjtcblxuXG4gXHQvLyBMb2FkIGVudHJ5IG1vZHVsZSBhbmQgcmV0dXJuIGV4cG9ydHNcbiBcdHJldHVybiBfX3dlYnBhY2tfcmVxdWlyZV9fKF9fd2VicGFja19yZXF1aXJlX18ucyA9IFwiLi9zcmMvcHJvamVjdF9saXN0LnRzXCIpO1xuIiwiY29uc3QgZmlsdGVyQmFyID0gZG9jdW1lbnQucXVlcnlTZWxlY3RvcihcIiNmaWx0ZXItYmFyXCIpO1xuY29uc3QgdGlsZUNvbnRhaW5lciA9IGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3IoXCIjdGlsZS1jb250YWluZXJcIik7XG5lbnVtIFBoYXNlT3JkZXIge1xuICAgIHByb3NwZWN0aXZlLFxuICAgIHRlbmRlcmluZyxcbiAgICBwbGFubmluZyxcbiAgICBleGVjdXRpbmcsXG4gICAgc2V0dGxlbWVudCxcbiAgICB3YXJyYW50eSxcbiAgICBmaW5pc2hlZCxcbn1cbmVudW0gU29ydEJ1dHRvblR5cGUge1xuICAgIGlkID0gXCJpZFwiLFxuICAgIG5hbWUgPSBcIm5hbWVcIixcbiAgICBwaGFzZSA9IFwicGhhc2VcIixcbn1cblxudHlwZSBTb3J0QnV0dG9uU3RhdGUgPSB7XG4gICAgdHlwZTogc3RyaW5nO1xuICAgIGFzYzogYm9vbGVhbjtcbn07XG50eXBlIFBoYXNlQnV0dG9uU3RhdGUgPSB7XG4gICAgcGhhc2U6IHN0cmluZztcbiAgICBoaWRlUGhhc2U6IGJvb2xlYW47XG59O1xuXG5jbGFzcyBTeXN0b3JpUHJvamVjdFRpbGUgZXh0ZW5kcyBIVE1MRWxlbWVudCB7XG4gICAgY29uc3RydWN0b3IoKSB7XG4gICAgICAgIHN1cGVyKCk7XG4gICAgfVxuICAgIGdldCBwaygpOiBudW1iZXIge1xuICAgICAgICByZXR1cm4gcGFyc2VJbnQodGhpcy5kYXRhc2V0W1wicGtcIl0hKTtcbiAgICB9XG4gICAgZ2V0IG5hbWUoKTogc3RyaW5nIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuZGF0YXNldFtcIm5hbWVcIl0hO1xuICAgIH1cbiAgICBnZXQgcGhhc2UoKTogUGhhc2VPcmRlciB7XG4gICAgICAgIHJldHVybiAodGhpcy5kYXRhc2V0W1wicGhhc2VcIl0gfHwgUGhhc2VPcmRlci5wcm9zcGVjdGl2ZSkgYXMgUGhhc2VPcmRlcjtcbiAgICB9XG5cbiAgICBnZXQgaGlkZGVuKCk6IGJvb2xlYW4ge1xuICAgICAgICByZXR1cm4gdGhpcy5jbGFzc0xpc3QuY29udGFpbnMoXCJoaWRkZW5cIikgPT09IHRydWU7XG4gICAgfVxuICAgIGhpZGUoaGlkZTogYm9vbGVhbik6IHZvaWQge1xuICAgICAgICBoaWRlID8gdGhpcy5jbGFzc0xpc3QuYWRkKFwiaGlkZGVuXCIpIDogdGhpcy5jbGFzc0xpc3QucmVtb3ZlKFwiaGlkZGVuXCIpO1xuICAgIH1cbn1cblxuY2xhc3MgU3lzdG9yaVNvcnRCdXR0b24gZXh0ZW5kcyBIVE1MRWxlbWVudCB7XG4gICAgY29uc3RydWN0b3IoKSB7XG4gICAgICAgIHN1cGVyKCk7XG4gICAgICAgIHRoaXMuYWRkRXZlbnRMaXN0ZW5lcihcImNsaWNrXCIsICgpID0+IHRoaXMuc29ydFByb2plY3RUaWxlcyh0cnVlKSk7XG4gICAgfVxuICAgIGdldCB0eXBlKCk6IFNvcnRCdXR0b25UeXBlIHtcbiAgICAgICAgc3dpdGNoICh0aGlzLmRhdGFzZXRbXCJ0eXBlXCJdKSB7XG4gICAgICAgICAgICBjYXNlIFwiaWRcIjpcbiAgICAgICAgICAgICAgICByZXR1cm4gU29ydEJ1dHRvblR5cGUuaWQ7XG4gICAgICAgICAgICBjYXNlIFwibmFtZVwiOlxuICAgICAgICAgICAgICAgIHJldHVybiBTb3J0QnV0dG9uVHlwZS5uYW1lO1xuICAgICAgICAgICAgY2FzZSBcInBoYXNlXCI6XG4gICAgICAgICAgICAgICAgcmV0dXJuIFNvcnRCdXR0b25UeXBlLnBoYXNlO1xuICAgICAgICAgICAgZGVmYXVsdDpcbiAgICAgICAgICAgICAgICB0aHJvdyBFcnJvcihcIkNvdWxkbid0IGNhdGNoIFNvcnRCdXR0b25UeXBlLlwiKTtcbiAgICAgICAgfVxuICAgIH1cbiAgICBzZXQgdHlwZSh0eXBlOiBTb3J0QnV0dG9uVHlwZSkge1xuICAgICAgICB0aGlzLmRhdGFzZXRbXCJ0eXBlXCJdID0gU29ydEJ1dHRvblR5cGVbdHlwZV07XG4gICAgfVxuXG4gICAgLy8gQVNDL0RFU0Mgc29ydGluZyBvcmRlclxuICAgIGdldCBhc2MoKTogYm9vbGVhbiB7XG4gICAgICAgIHJldHVybiB0aGlzLmRhdGFzZXRbXCJhc2NcIl0gPT0gXCJ0cnVlXCI7XG4gICAgfVxuICAgIHNldCBhc2MoYXNjOiBib29sZWFuKSB7XG4gICAgICAgIGFzYyA/ICh0aGlzLmRhdGFzZXRbXCJhc2NcIl0gPSBcInRydWVcIikgOiAodGhpcy5kYXRhc2V0W1wiYXNjXCJdID0gXCJmYWxzZVwiKTtcbiAgICB9XG4gICAgdG9nZ2xlQXNjKCk6IHZvaWQge1xuICAgICAgICB0aGlzLmFzYyA9ICF0aGlzLmFzYztcbiAgICB9XG5cbiAgICBnZXQgYWN0aXZlKCk6IGJvb2xlYW4ge1xuICAgICAgICByZXR1cm4gdGhpcy5jbGFzc0xpc3QuY29udGFpbnMoXCJhY3RpdmVcIik7XG4gICAgfVxuICAgIHNldCBhY3RpdmUoc3RhdHVzOiBib29sZWFuKSB7XG4gICAgICAgIHN0YXR1cyA/IHRoaXMuY2xhc3NMaXN0LmFkZChcImFjdGl2ZVwiKSA6IHRoaXMuY2xhc3NMaXN0LnJlbW92ZShcImFjdGl2ZVwiKTtcbiAgICB9XG5cbiAgICAvLyBhZGRzIGNsYXNzIGBhY3RpdmVgIHRvIGFjdGl2ZSBidXR0b24gYW5kIHJlbW92ZXMgaXQgZnJvbSBhbGwgb3RoZXJzLlxuICAgIGFjdGl2YXRlRXhjbHVzaXZlKCk6IHZvaWQge1xuICAgICAgICBjb25zdCBidG5zOiBTeXN0b3JpU29ydEJ1dHRvbltdID0gQXJyYXkuZnJvbShcbiAgICAgICAgICAgIGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGwoXCJzeXMtc29ydC1idXR0b25cIiksXG4gICAgICAgICk7XG4gICAgICAgIGZvciAoY29uc3QgYnRuIG9mIGJ0bnMpIHtcbiAgICAgICAgICAgIGJ0bi5hY3RpdmUgPSBmYWxzZTtcbiAgICAgICAgfVxuICAgICAgICB0aGlzLmFjdGl2ZSA9IHRydWU7XG4gICAgfVxuXG4gICAgc29ydFByb2plY3RUaWxlcyh0b2dnbGVBc2M6IGJvb2xlYW4pOiB2b2lkIHtcbiAgICAgICAgLy8gc3RhcnRpbmcgd2l0aCB0b2dnbGluZyBzb3J0aW5nIG9yZGVyLCBtb3ZlIHRvIGJvdHRvbSB0byBleGNoYW5nZSB0cnVlL2ZhbHNlIGJlaGF2aW91clxuICAgICAgICBpZiAodG9nZ2xlQXNjKSB0aGlzLnRvZ2dsZUFzYygpO1xuICAgICAgICB0aGlzLmFjdGl2YXRlRXhjbHVzaXZlKCk7XG5cbiAgICAgICAgY29uc3QgcHJvamVjdFRpbGVzID0gQXJyYXkuZnJvbShcbiAgICAgICAgICAgIGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGw8U3lzdG9yaVByb2plY3RUaWxlPihcIi50aWxlXCIpLFxuICAgICAgICApO1xuXG4gICAgICAgIHByb2plY3RUaWxlcy5zb3J0KChhLCBiKSA9PiB7XG4gICAgICAgICAgICBzd2l0Y2ggKHRoaXMudHlwZSkge1xuICAgICAgICAgICAgICAgIGNhc2UgU29ydEJ1dHRvblR5cGUuaWQ6XG4gICAgICAgICAgICAgICAgICAgIGlmICh0aGlzLmFzYykge1xuICAgICAgICAgICAgICAgICAgICAgICAgcmV0dXJuIGIucGsgPCBhLnBrID8gLTEgOiAxO1xuICAgICAgICAgICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgICAgICAgICAgcmV0dXJuIGEucGsgPCBiLnBrID8gLTEgOiAxO1xuICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgY2FzZSBTb3J0QnV0dG9uVHlwZS5uYW1lOlxuICAgICAgICAgICAgICAgICAgICBpZiAodGhpcy5hc2MpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIHJldHVybiBhLm5hbWUubG9jYWxlQ29tcGFyZShiLm5hbWUpO1xuICAgICAgICAgICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgICAgICAgICAgcmV0dXJuIGIubmFtZS5sb2NhbGVDb21wYXJlKGEubmFtZSk7XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICBjYXNlIFNvcnRCdXR0b25UeXBlLnBoYXNlOlxuICAgICAgICAgICAgICAgICAgICBpZiAodGhpcy5hc2MpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIHJldHVybiBQaGFzZU9yZGVyW2IucGhhc2VdIDw9IFBoYXNlT3JkZXJbYS5waGFzZV1cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICA/IC0xXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgOiAxO1xuICAgICAgICAgICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgICAgICAgICAgcmV0dXJuIFBoYXNlT3JkZXJbYS5waGFzZV0gPD0gUGhhc2VPcmRlcltiLnBoYXNlXVxuICAgICAgICAgICAgICAgICAgICAgICAgICAgID8gLTFcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICA6IDE7XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICBkZWZhdWx0OlxuICAgICAgICAgICAgICAgICAgICB0aHJvdyBuZXcgRXJyb3IoXG4gICAgICAgICAgICAgICAgICAgICAgICBgQ2FuJ3QgZmluZCBhIFNvcnRCdXR0b25UeXBlIHR5cGUgZm9yICR7dGhpcy50eXBlfS5gLFxuICAgICAgICAgICAgICAgICAgICApO1xuICAgICAgICAgICAgfVxuICAgICAgICB9KTtcblxuICAgICAgICBpZiAodGlsZUNvbnRhaW5lcikge1xuICAgICAgICAgICAgdGlsZUNvbnRhaW5lci5pbm5lckhUTUwgPSBcIlwiO1xuICAgICAgICAgICAgZm9yIChjb25zdCB0aWxlIG9mIHByb2plY3RUaWxlcykge1xuICAgICAgICAgICAgICAgIHRpbGVDb250YWluZXIuYXBwZW5kQ2hpbGQodGlsZSk7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cblxuICAgICAgICB0aGlzLnNhdmVTdGF0ZVRvTG9jYWxTdG9yYWdlKCk7XG4gICAgfVxuXG4gICAgc2F2ZVN0YXRlVG9Mb2NhbFN0b3JhZ2UoKTogdm9pZCB7XG4gICAgICAgIGxvY2FsU3RvcmFnZS5zZXRJdGVtKFxuICAgICAgICAgICAgXCJzdGF0ZS1TeXN0b3JpU29ydEJ1dHRvblwiLFxuICAgICAgICAgICAgSlNPTi5zdHJpbmdpZnkoe1xuICAgICAgICAgICAgICAgIHR5cGU6IHRoaXMudHlwZSxcbiAgICAgICAgICAgICAgICBhc2M6IHRoaXMuYXNjLFxuICAgICAgICAgICAgfSksXG4gICAgICAgICk7XG4gICAgfVxufVxuXG5mdW5jdGlvbiBzYXZlUGhhc2VTdGF0ZVRvTG9jYWxTdG9yYWdlKCk6IHZvaWQge1xuICAgIGNvbnN0IGJ0bnM6IFN5c3RvcmlQaGFzZUJ1dHRvbltdID0gQXJyYXkuZnJvbShcbiAgICAgICAgZG9jdW1lbnQucXVlcnlTZWxlY3RvckFsbChcInN5cy1waGFzZS1idXR0b25cIiksXG4gICAgKTtcbiAgICBjb25zdCBidG5zU3RhdGU6IFBoYXNlQnV0dG9uU3RhdGVbXSA9IFtdO1xuICAgIGZvciAoY29uc3QgYnRuIG9mIGJ0bnMpIHtcbiAgICAgICAgYnRuc1N0YXRlLnB1c2goeyBwaGFzZTogYnRuLnBoYXNlLCBoaWRlUGhhc2U6IGJ0bi5oaWRlUGhhc2UgfSk7XG4gICAgfVxuICAgIGxvY2FsU3RvcmFnZS5zZXRJdGVtKFwic3RhdGUtU3lzdG9yaVBoYXNlQnV0dG9uXCIsIEpTT04uc3RyaW5naWZ5KGJ0bnNTdGF0ZSkpO1xufVxuXG5jbGFzcyBTeXN0b3JpUGhhc2VCdXR0b24gZXh0ZW5kcyBIVE1MRWxlbWVudCB7XG4gICAgY29uc3RydWN0b3IoKSB7XG4gICAgICAgIHN1cGVyKCk7XG4gICAgICAgIHRoaXMuYWRkRXZlbnRMaXN0ZW5lcihcImNsaWNrXCIsICgpID0+IHRoaXMuZmlsdGVyUHJvamVjdFRpbGVzKHRydWUpKTtcbiAgICB9XG5cbiAgICBnZXQgcGhhc2UoKTogc3RyaW5nIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuZGF0YXNldFtcInBoYXNlXCJdITtcbiAgICB9XG4gICAgc2V0IHBoYXNlKHBoYXNlOiBzdHJpbmcpIHtcbiAgICAgICAgdGhpcy5kYXRhc2V0W1wicGhhc2VcIl0gPSBwaGFzZTtcbiAgICB9XG5cbiAgICAvLyBoaWRlUGhhc2UgPT09IGhpZGRlblxuICAgIGdldCBoaWRlUGhhc2UoKTogYm9vbGVhbiB7XG4gICAgICAgIHJldHVybiB0aGlzLmNsYXNzTGlzdC5jb250YWlucyhcImhpZGUtcGhhc2VcIik7XG4gICAgfVxuICAgIHNldCBoaWRlUGhhc2UoaGlkZTogYm9vbGVhbikge1xuICAgICAgICBoaWRlXG4gICAgICAgICAgICA/IHRoaXMuY2xhc3NMaXN0LmFkZChcImhpZGUtcGhhc2VcIilcbiAgICAgICAgICAgIDogdGhpcy5jbGFzc0xpc3QucmVtb3ZlKFwiaGlkZS1waGFzZVwiKTtcbiAgICB9XG5cbiAgICB0b2dnbGVQcm9qZWN0VGlsZXMoaGlkZTogYm9vbGVhbik6IHZvaWQge1xuICAgICAgICBjb25zdCBwcm9qZWN0VGlsZXM6IFN5c3RvcmlQcm9qZWN0VGlsZVtdID0gQXJyYXkuZnJvbShcbiAgICAgICAgICAgIGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGwoXG4gICAgICAgICAgICAgICAgYHN5cy1wcm9qZWN0LXRpbGVbZGF0YS1waGFzZT0ke3RoaXMucGhhc2V9XWAsXG4gICAgICAgICAgICApLFxuICAgICAgICApO1xuICAgICAgICBmb3IgKGNvbnN0IHRpbGUgb2YgcHJvamVjdFRpbGVzKSB7XG4gICAgICAgICAgICB0aWxlLmhpZGUoaGlkZSk7XG4gICAgICAgIH1cbiAgICAgICAgc2F2ZVBoYXNlU3RhdGVUb0xvY2FsU3RvcmFnZSgpO1xuICAgIH1cblxuICAgIGZpbHRlclByb2plY3RUaWxlcyh0b2dnbGU6IGJvb2xlYW4pOiB2b2lkIHtcbiAgICAgICAgaWYgKHRvZ2dsZSkgdGhpcy5oaWRlUGhhc2UgPSAhdGhpcy5oaWRlUGhhc2U7XG4gICAgICAgIHRoaXMuaGlkZVBoYXNlXG4gICAgICAgICAgICA/IHRoaXMudG9nZ2xlUHJvamVjdFRpbGVzKHRydWUpXG4gICAgICAgICAgICA6IHRoaXMudG9nZ2xlUHJvamVjdFRpbGVzKGZhbHNlKTtcbiAgICB9XG59XG5cbmNsYXNzIFN5c3RvcmlTZWFyY2hFbGVtZW50IGV4dGVuZHMgSFRNTEVsZW1lbnQge1xuICAgIC8vIFRoaXMgY3VzdG9tIGVsZW1lbnQgaXMgZm9yIGNvbXBvc2luZyB0aGUgdHdvIGNoaWxkTm9kZXMuXG4gICAgY29uc3RydWN0b3IoKSB7XG4gICAgICAgIHN1cGVyKCk7XG4gICAgfVxufVxuXG5jbGFzcyBTeXN0b3JpU2VhcmNoSW5wdXQgZXh0ZW5kcyBIVE1MSW5wdXRFbGVtZW50IHtcbiAgICBjb25zdHJ1Y3RvcigpIHtcbiAgICAgICAgc3VwZXIoKTtcbiAgICAgICAgdGhpcy5hZGRFdmVudExpc3RlbmVyKFwia2V5dXBcIiwgKCkgPT4gdGhpcy5hcGlTZWFyY2hQcm9qZWN0cygpKTtcbiAgICB9XG5cbiAgICBhcGlTZWFyY2hQcm9qZWN0cygpOiBudW1iZXJbXSB7XG4gICAgICAgIGNvbnN0IHByb2plY3RzID0gW10gYXMgbnVtYmVyW107XG4gICAgICAgIHByb2plY3RzLnB1c2goMTEpO1xuICAgICAgICBwcm9qZWN0cy5wdXNoKDIzKTtcbiAgICAgICAgcmV0dXJuIHByb2plY3RzO1xuICAgIH1cbn1cblxuZnVuY3Rpb24gbG9hZExvY2FsU3RvcmFnZSgpOiB2b2lkIHtcbiAgICBjb25zdCBzb3J0SnNvbiA9IGxvY2FsU3RvcmFnZS5nZXRJdGVtKFwic3RhdGUtU3lzdG9yaVNvcnRCdXR0b25cIik7XG4gICAgY29uc3QgcGhhc2VKc29uID0gbG9jYWxTdG9yYWdlLmdldEl0ZW0oXCJzdGF0ZS1TeXN0b3JpUGhhc2VCdXR0b25cIik7XG4gICAgaWYgKHNvcnRKc29uKSB7XG4gICAgICAgIGNvbnN0IHN0YXRlOiBTb3J0QnV0dG9uU3RhdGUgPSBKU09OLnBhcnNlKHNvcnRKc29uKTtcbiAgICAgICAgY29uc3QgYnRuczogU3lzdG9yaVNvcnRCdXR0b25bXSA9IEFycmF5LmZyb20oXG4gICAgICAgICAgICBkb2N1bWVudC5xdWVyeVNlbGVjdG9yQWxsKFwic3lzLXNvcnQtYnV0dG9uXCIpLFxuICAgICAgICApO1xuICAgICAgICBmb3IgKGNvbnN0IGJ0biBvZiBidG5zKSB7XG4gICAgICAgICAgICBpZiAoYnRuLnR5cGUgPT09IHN0YXRlLnR5cGUpIHtcbiAgICAgICAgICAgICAgICBjb25zb2xlLmxvZyhgbG9hZGluZyBmcm9tIGxvY2FsU3RvcmFnZSBmb3IgJHtidG4udHlwZX0uYCk7XG4gICAgICAgICAgICAgICAgYnRuLmFzYyA9IHN0YXRlLmFzYztcbiAgICAgICAgICAgICAgICBidG4uc29ydFByb2plY3RUaWxlcyhmYWxzZSk7XG4gICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgIGJ0bi5hY3RpdmUgPSBmYWxzZTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgIH1cbiAgICBpZiAocGhhc2VKc29uKSB7XG4gICAgICAgIGNvbnN0IHN0YXRlOiBQaGFzZUJ1dHRvblN0YXRlW10gPSBKU09OLnBhcnNlKHBoYXNlSnNvbik7XG4gICAgICAgIGNvbnN0IGJ0bnM6IFN5c3RvcmlQaGFzZUJ1dHRvbltdID0gQXJyYXkuZnJvbShcbiAgICAgICAgICAgIGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGwoXCJzeXMtcGhhc2UtYnV0dG9uXCIpLFxuICAgICAgICApO1xuICAgICAgICBmb3IgKGNvbnN0IHAgb2Ygc3RhdGUpIHtcbiAgICAgICAgICAgIGlmIChwLmhpZGVQaGFzZSkge1xuICAgICAgICAgICAgICAgIGZvciAoY29uc3QgYnRuIG9mIGJ0bnMpIHtcbiAgICAgICAgICAgICAgICAgICAgaWYgKGJ0bi5waGFzZSA9PT0gcC5waGFzZSkge1xuICAgICAgICAgICAgICAgICAgICAgICAgYnRuLmhpZGVQaGFzZSA9IHAuaGlkZVBoYXNlO1xuICAgICAgICAgICAgICAgICAgICAgICAgYnRuLmZpbHRlclByb2plY3RUaWxlcyhmYWxzZSk7XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICB9XG59XG5cbmN1c3RvbUVsZW1lbnRzLmRlZmluZShcInN5cy1zZWFyY2gtaW5wdXRcIiwgU3lzdG9yaVNlYXJjaElucHV0LCB7XG4gICAgZXh0ZW5kczogXCJpbnB1dFwiLFxufSk7XG5jdXN0b21FbGVtZW50cy5kZWZpbmUoXCJzeXMtc2VhcmNoLWVsZW1lbnRcIiwgU3lzdG9yaVNlYXJjaEVsZW1lbnQpO1xuY3VzdG9tRWxlbWVudHMuZGVmaW5lKFwic3lzLXBoYXNlLWJ1dHRvblwiLCBTeXN0b3JpUGhhc2VCdXR0b24pO1xuY3VzdG9tRWxlbWVudHMuZGVmaW5lKFwic3lzLXNvcnQtYnV0dG9uXCIsIFN5c3RvcmlTb3J0QnV0dG9uKTtcbmN1c3RvbUVsZW1lbnRzLmRlZmluZShcInN5cy1wcm9qZWN0LXRpbGVcIiwgU3lzdG9yaVByb2plY3RUaWxlKTtcblxubG9hZExvY2FsU3RvcmFnZSgpO1xuaWYgKGZpbHRlckJhcikge1xuICAgIGZpbHRlckJhci5jbGFzc0xpc3QucmVtb3ZlKFwiaGlkZGVuXCIpO1xufVxuaWYgKHRpbGVDb250YWluZXIpIHtcbiAgICB0aWxlQ29udGFpbmVyLmNsYXNzTGlzdC5yZW1vdmUoXCJoaWRkZW5cIik7XG59XG4iXSwic291cmNlUm9vdCI6IiJ9