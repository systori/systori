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
        return parseInt(this.dataset.pk);
    }
    get name() {
        return this.dataset.name;
    }
    get phase() {
        return (this.dataset.phase || PhaseOrder.prospective);
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
        switch (this.dataset.type) {
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
        this.dataset.type = SortButtonType[type];
    }
    // ASC/DESC sorting order
    get asc() {
        return this.dataset.asc == "true";
    }
    set asc(asc) {
        asc ? (this.dataset.asc = "true") : (this.dataset.asc = "false");
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
            active: this.active,
        }));
    }
    _loadStateFromLocalStorage() {
        console.log(`SystoriSortButton type==${this.type} active state==${this.active}.`, `background: fuchsia; color: #3e3e3e`);
        // check if custom element is bound to dom
        if (this.active || !this.active) {
            const sortJson = localStorage.getItem("state-SystoriSortButton");
            if (sortJson) {
                const state = JSON.parse(sortJson);
                console.info(`SystoriSortButton type==${this.type} localStorage active state==${state.active}.`);
                if (this.type === state.type) {
                    this.asc = state.asc;
                    this.sortProjectTiles(false);
                }
                else {
                    this.active = false;
                }
            }
        }
    }
    connectedCallback() {
        console.info(`SystoriSortButton type==${this.type} was attached.`);
        this._loadStateFromLocalStorage();
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
        return this.dataset.phase;
    }
    set phase(phase) {
        this.dataset.phase = phase;
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
    // const sortJson = localStorage.getItem("state-SystoriSortButton");
    const phaseJson = localStorage.getItem("state-SystoriPhaseButton");
    // if (sortJson) {
    //     const state: SortButtonState = JSON.parse(sortJson);
    //     const btns: SystoriSortButton[] = Array.from(
    //         document.querySelectorAll("sys-sort-button"),
    //     );
    //     for (const btn of btns) {
    //         if (btn.type === state.type) {
    //             btn.asc = state.asc;
    //             btn.sortProjectTiles(false);
    //         } else {
    //             btn.active = false;
    //         }
    //     }
    // }
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
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8vd2VicGFjay9ib290c3RyYXAiLCJ3ZWJwYWNrOi8vLy4vc3JjL3Byb2plY3RfbGlzdC50cyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiO1FBQUE7UUFDQTs7UUFFQTtRQUNBOztRQUVBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBOztRQUVBO1FBQ0E7O1FBRUE7UUFDQTs7UUFFQTtRQUNBO1FBQ0E7OztRQUdBO1FBQ0E7O1FBRUE7UUFDQTs7UUFFQTtRQUNBO1FBQ0E7UUFDQSwwQ0FBMEMsZ0NBQWdDO1FBQzFFO1FBQ0E7O1FBRUE7UUFDQTtRQUNBO1FBQ0Esd0RBQXdELGtCQUFrQjtRQUMxRTtRQUNBLGlEQUFpRCxjQUFjO1FBQy9EOztRQUVBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQSx5Q0FBeUMsaUNBQWlDO1FBQzFFLGdIQUFnSCxtQkFBbUIsRUFBRTtRQUNySTtRQUNBOztRQUVBO1FBQ0E7UUFDQTtRQUNBLDJCQUEyQiwwQkFBMEIsRUFBRTtRQUN2RCxpQ0FBaUMsZUFBZTtRQUNoRDtRQUNBO1FBQ0E7O1FBRUE7UUFDQSxzREFBc0QsK0RBQStEOztRQUVySDtRQUNBOzs7UUFHQTtRQUNBOzs7Ozs7Ozs7Ozs7OztBQ2xGQSxNQUFNLFNBQVMsR0FBRyxRQUFRLENBQUMsYUFBYSxDQUFDLGFBQWEsQ0FBQyxDQUFDO0FBQ3hELE1BQU0sYUFBYSxHQUFHLFFBQVEsQ0FBQyxhQUFhLENBQUMsaUJBQWlCLENBQUMsQ0FBQztBQUNoRSxJQUFLLFVBUUo7QUFSRCxXQUFLLFVBQVU7SUFDWCx5REFBVztJQUNYLHFEQUFTO0lBQ1QsbURBQVE7SUFDUixxREFBUztJQUNULHVEQUFVO0lBQ1YsbURBQVE7SUFDUixtREFBUTtBQUNaLENBQUMsRUFSSSxVQUFVLEtBQVYsVUFBVSxRQVFkO0FBQ0QsSUFBSyxjQUlKO0FBSkQsV0FBSyxjQUFjO0lBQ2YsMkJB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QyxTQUFTLENBQUMsTUFBTSxDQUFDLFFBQVEsQ0FBQyxDQUFDO0NBQzVDIiwiZmlsZSI6InByb2plY3RfbGlzdC5qcyIsInNvdXJjZXNDb250ZW50IjpbIiBcdC8vIFRoZSBtb2R1bGUgY2FjaGVcbiBcdHZhciBpbnN0YWxsZWRNb2R1bGVzID0ge307XG5cbiBcdC8vIFRoZSByZXF1aXJlIGZ1bmN0aW9uXG4gXHRmdW5jdGlvbiBfX3dlYnBhY2tfcmVxdWlyZV9fKG1vZHVsZUlkKSB7XG5cbiBcdFx0Ly8gQ2hlY2sgaWYgbW9kdWxlIGlzIGluIGNhY2hlXG4gXHRcdGlmKGluc3RhbGxlZE1vZHVsZXNbbW9kdWxlSWRdKSB7XG4gXHRcdFx0cmV0dXJuIGluc3RhbGxlZE1vZHVsZXNbbW9kdWxlSWRdLmV4cG9ydHM7XG4gXHRcdH1cbiBcdFx0Ly8gQ3JlYXRlIGEgbmV3IG1vZHVsZSAoYW5kIHB1dCBpdCBpbnRvIHRoZSBjYWNoZSlcbiBcdFx0dmFyIG1vZHVsZSA9IGluc3RhbGxlZE1vZHVsZXNbbW9kdWxlSWRdID0ge1xuIFx0XHRcdGk6IG1vZHVsZUlkLFxuIFx0XHRcdGw6IGZhbHNlLFxuIFx0XHRcdGV4cG9ydHM6IHt9XG4gXHRcdH07XG5cbiBcdFx0Ly8gRXhlY3V0ZSB0aGUgbW9kdWxlIGZ1bmN0aW9uXG4gXHRcdG1vZHVsZXNbbW9kdWxlSWRdLmNhbGwobW9kdWxlLmV4cG9ydHMsIG1vZHVsZSwgbW9kdWxlLmV4cG9ydHMsIF9fd2VicGFja19yZXF1aXJlX18pO1xuXG4gXHRcdC8vIEZsYWcgdGhlIG1vZHVsZSBhcyBsb2FkZWRcbiBcdFx0bW9kdWxlLmwgPSB0cnVlO1xuXG4gXHRcdC8vIFJldHVybiB0aGUgZXhwb3J0cyBvZiB0aGUgbW9kdWxlXG4gXHRcdHJldHVybiBtb2R1bGUuZXhwb3J0cztcbiBcdH1cblxuXG4gXHQvLyBleHBvc2UgdGhlIG1vZHVsZXMgb2JqZWN0IChfX3dlYnBhY2tfbW9kdWxlc19fKVxuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy5tID0gbW9kdWxlcztcblxuIFx0Ly8gZXhwb3NlIHRoZSBtb2R1bGUgY2FjaGVcbiBcdF9fd2VicGFja19yZXF1aXJlX18uYyA9IGluc3RhbGxlZE1vZHVsZXM7XG5cbiBcdC8vIGRlZmluZSBnZXR0ZXIgZnVuY3Rpb24gZm9yIGhhcm1vbnkgZXhwb3J0c1xuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy5kID0gZnVuY3Rpb24oZXhwb3J0cywgbmFtZSwgZ2V0dGVyKSB7XG4gXHRcdGlmKCFfX3dlYnBhY2tfcmVxdWlyZV9fLm8oZXhwb3J0cywgbmFtZSkpIHtcbiBcdFx0XHRPYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgbmFtZSwgeyBlbnVtZXJhYmxlOiB0cnVlLCBnZXQ6IGdldHRlciB9KTtcbiBcdFx0fVxuIFx0fTtcblxuIFx0Ly8gZGVmaW5lIF9fZXNNb2R1bGUgb24gZXhwb3J0c1xuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy5yID0gZnVuY3Rpb24oZXhwb3J0cykge1xuIFx0XHRpZih0eXBlb2YgU3ltYm9sICE9PSAndW5kZWZpbmVkJyAmJiBTeW1ib2wudG9TdHJpbmdUYWcpIHtcbiBcdFx0XHRPYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgU3ltYm9sLnRvU3RyaW5nVGFnLCB7IHZhbHVlOiAnTW9kdWxlJyB9KTtcbiBcdFx0fVxuIFx0XHRPYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgJ19fZXNNb2R1bGUnLCB7IHZhbHVlOiB0cnVlIH0pO1xuIFx0fTtcblxuIFx0Ly8gY3JlYXRlIGEgZmFrZSBuYW1lc3BhY2Ugb2JqZWN0XG4gXHQvLyBtb2RlICYgMTogdmFsdWUgaXMgYSBtb2R1bGUgaWQsIHJlcXVpcmUgaXRcbiBcdC8vIG1vZGUgJiAyOiBtZXJnZSBhbGwgcHJvcGVydGllcyBvZiB2YWx1ZSBpbnRvIHRoZSBuc1xuIFx0Ly8gbW9kZSAmIDQ6IHJldHVybiB2YWx1ZSB3aGVuIGFscmVhZHkgbnMgb2JqZWN0XG4gXHQvLyBtb2RlICYgOHwxOiBiZWhhdmUgbGlrZSByZXF1aXJlXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLnQgPSBmdW5jdGlvbih2YWx1ZSwgbW9kZSkge1xuIFx0XHRpZihtb2RlICYgMSkgdmFsdWUgPSBfX3dlYnBhY2tfcmVxdWlyZV9fKHZhbHVlKTtcbiBcdFx0aWYobW9kZSAmIDgpIHJldHVybiB2YWx1ZTtcbiBcdFx0aWYoKG1vZGUgJiA0KSAmJiB0eXBlb2YgdmFsdWUgPT09ICdvYmplY3QnICYmIHZhbHVlICYmIHZhbHVlLl9fZXNNb2R1bGUpIHJldHVybiB2YWx1ZTtcbiBcdFx0dmFyIG5zID0gT2JqZWN0LmNyZWF0ZShudWxsKTtcbiBcdFx0X193ZWJwYWNrX3JlcXVpcmVfXy5yKG5zKTtcbiBcdFx0T2JqZWN0LmRlZmluZVByb3BlcnR5KG5zLCAnZGVmYXVsdCcsIHsgZW51bWVyYWJsZTogdHJ1ZSwgdmFsdWU6IHZhbHVlIH0pO1xuIFx0XHRpZihtb2RlICYgMiAmJiB0eXBlb2YgdmFsdWUgIT0gJ3N0cmluZycpIGZvcih2YXIga2V5IGluIHZhbHVlKSBfX3dlYnBhY2tfcmVxdWlyZV9fLmQobnMsIGtleSwgZnVuY3Rpb24oa2V5KSB7IHJldHVybiB2YWx1ZVtrZXldOyB9LmJpbmQobnVsbCwga2V5KSk7XG4gXHRcdHJldHVybiBucztcbiBcdH07XG5cbiBcdC8vIGdldERlZmF1bHRFeHBvcnQgZnVuY3Rpb24gZm9yIGNvbXBhdGliaWxpdHkgd2l0aCBub24taGFybW9ueSBtb2R1bGVzXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLm4gPSBmdW5jdGlvbihtb2R1bGUpIHtcbiBcdFx0dmFyIGdldHRlciA9IG1vZHVsZSAmJiBtb2R1bGUuX19lc01vZHVsZSA/XG4gXHRcdFx0ZnVuY3Rpb24gZ2V0RGVmYXVsdCgpIHsgcmV0dXJuIG1vZHVsZVsnZGVmYXVsdCddOyB9IDpcbiBcdFx0XHRmdW5jdGlvbiBnZXRNb2R1bGVFeHBvcnRzKCkgeyByZXR1cm4gbW9kdWxlOyB9O1xuIFx0XHRfX3dlYnBhY2tfcmVxdWlyZV9fLmQoZ2V0dGVyLCAnYScsIGdldHRlcik7XG4gXHRcdHJldHVybiBnZXR0ZXI7XG4gXHR9O1xuXG4gXHQvLyBPYmplY3QucHJvdG90eXBlLmhhc093blByb3BlcnR5LmNhbGxcbiBcdF9fd2VicGFja19yZXF1aXJlX18ubyA9IGZ1bmN0aW9uKG9iamVjdCwgcHJvcGVydHkpIHsgcmV0dXJuIE9iamVjdC5wcm90b3R5cGUuaGFzT3duUHJvcGVydHkuY2FsbChvYmplY3QsIHByb3BlcnR5KTsgfTtcblxuIFx0Ly8gX193ZWJwYWNrX3B1YmxpY19wYXRoX19cbiBcdF9fd2VicGFja19yZXF1aXJlX18ucCA9IFwiXCI7XG5cblxuIFx0Ly8gTG9hZCBlbnRyeSBtb2R1bGUgYW5kIHJldHVybiBleHBvcnRzXG4gXHRyZXR1cm4gX193ZWJwYWNrX3JlcXVpcmVfXyhfX3dlYnBhY2tfcmVxdWlyZV9fLnMgPSBcIi4vc3JjL3Byb2plY3RfbGlzdC50c1wiKTtcbiIsImNvbnN0IGZpbHRlckJhciA9IGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3IoXCIjZmlsdGVyLWJhclwiKTtcbmNvbnN0IHRpbGVDb250YWluZXIgPSBkb2N1bWVudC5xdWVyeVNlbGVjdG9yKFwiI3RpbGUtY29udGFpbmVyXCIpO1xuZW51bSBQaGFzZU9yZGVyIHtcbiAgICBwcm9zcGVjdGl2ZSxcbiAgICB0ZW5kZXJpbmcsXG4gICAgcGxhbm5pbmcsXG4gICAgZXhlY3V0aW5nLFxuICAgIHNldHRsZW1lbnQsXG4gICAgd2FycmFudHksXG4gICAgZmluaXNoZWQsXG59XG5lbnVtIFNvcnRCdXR0b25UeXBlIHtcbiAgICBpZCA9IFwiaWRcIixcbiAgICBuYW1lID0gXCJuYW1lXCIsXG4gICAgcGhhc2UgPSBcInBoYXNlXCIsXG59XG5cbnR5cGUgU29ydEJ1dHRvblN0YXRlID0ge1xuICAgIHR5cGU6IFNvcnRCdXR0b25UeXBlO1xuICAgIGFzYzogYm9vbGVhbjtcbiAgICBhY3RpdmU6IGJvb2xlYW47XG59O1xudHlwZSBQaGFzZUJ1dHRvblN0YXRlID0ge1xuICAgIHBoYXNlOiBzdHJpbmc7XG4gICAgaGlkZVBoYXNlOiBib29sZWFuO1xufTtcblxuY2xhc3MgU3lzdG9yaVByb2plY3RUaWxlIGV4dGVuZHMgSFRNTEVsZW1lbnQge1xuICAgIGNvbnN0cnVjdG9yKCkge1xuICAgICAgICBzdXBlcigpO1xuICAgIH1cbiAgICBnZXQgcGsoKTogbnVtYmVyIHtcbiAgICAgICAgcmV0dXJuIHBhcnNlSW50KHRoaXMuZGF0YXNldC5wayEpO1xuICAgIH1cbiAgICBnZXQgbmFtZSgpOiBzdHJpbmcge1xuICAgICAgICByZXR1cm4gdGhpcy5kYXRhc2V0Lm5hbWUhO1xuICAgIH1cbiAgICBnZXQgcGhhc2UoKTogUGhhc2VPcmRlciB7XG4gICAgICAgIHJldHVybiAodGhpcy5kYXRhc2V0LnBoYXNlIHx8IFBoYXNlT3JkZXIucHJvc3BlY3RpdmUpIGFzIFBoYXNlT3JkZXI7XG4gICAgfVxuXG4gICAgZ2V0IGhpZGRlbigpOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuY2xhc3NMaXN0LmNvbnRhaW5zKFwiaGlkZGVuXCIpID09PSB0cnVlO1xuICAgIH1cbiAgICBoaWRlKGhpZGU6IGJvb2xlYW4pOiB2b2lkIHtcbiAgICAgICAgaGlkZSA/IHRoaXMuY2xhc3NMaXN0LmFkZChcImhpZGRlblwiKSA6IHRoaXMuY2xhc3NMaXN0LnJlbW92ZShcImhpZGRlblwiKTtcbiAgICB9XG59XG5cbmNsYXNzIFN5c3RvcmlTb3J0QnV0dG9uIGV4dGVuZHMgSFRNTEVsZW1lbnQge1xuICAgIGNvbnN0cnVjdG9yKCkge1xuICAgICAgICBzdXBlcigpO1xuICAgICAgICB0aGlzLmFkZEV2ZW50TGlzdGVuZXIoXCJjbGlja1wiLCAoKSA9PiB0aGlzLnNvcnRQcm9qZWN0VGlsZXModHJ1ZSkpO1xuICAgIH1cbiAgICBnZXQgdHlwZSgpOiBTb3J0QnV0dG9uVHlwZSB7XG4gICAgICAgIHN3aXRjaCAodGhpcy5kYXRhc2V0LnR5cGUpIHtcbiAgICAgICAgICAgIGNhc2UgXCJpZFwiOlxuICAgICAgICAgICAgICAgIHJldHVybiBTb3J0QnV0dG9uVHlwZS5pZDtcbiAgICAgICAgICAgIGNhc2UgXCJuYW1lXCI6XG4gICAgICAgICAgICAgICAgcmV0dXJuIFNvcnRCdXR0b25UeXBlLm5hbWU7XG4gICAgICAgICAgICBjYXNlIFwicGhhc2VcIjpcbiAgICAgICAgICAgICAgICByZXR1cm4gU29ydEJ1dHRvblR5cGUucGhhc2U7XG4gICAgICAgICAgICBkZWZhdWx0OlxuICAgICAgICAgICAgICAgIHRocm93IEVycm9yKFwiQ291bGRuJ3QgY2F0Y2ggU29ydEJ1dHRvblR5cGUuXCIpO1xuICAgICAgICB9XG4gICAgfVxuICAgIHNldCB0eXBlKHR5cGU6IFNvcnRCdXR0b25UeXBlKSB7XG4gICAgICAgIHRoaXMuZGF0YXNldC50eXBlID0gU29ydEJ1dHRvblR5cGVbdHlwZV07XG4gICAgfVxuXG4gICAgLy8gQVNDL0RFU0Mgc29ydGluZyBvcmRlclxuICAgIGdldCBhc2MoKTogYm9vbGVhbiB7XG4gICAgICAgIHJldHVybiB0aGlzLmRhdGFzZXQuYXNjID09IFwidHJ1ZVwiO1xuICAgIH1cbiAgICBzZXQgYXNjKGFzYzogYm9vbGVhbikge1xuICAgICAgICBhc2MgPyAodGhpcy5kYXRhc2V0LmFzYyA9IFwidHJ1ZVwiKSA6ICh0aGlzLmRhdGFzZXQuYXNjID0gXCJmYWxzZVwiKTtcbiAgICB9XG4gICAgdG9nZ2xlQXNjKCk6IHZvaWQge1xuICAgICAgICB0aGlzLmFzYyA9ICF0aGlzLmFzYztcbiAgICB9XG5cbiAgICBnZXQgYWN0aXZlKCk6IGJvb2xlYW4ge1xuICAgICAgICByZXR1cm4gdGhpcy5jbGFzc0xpc3QuY29udGFpbnMoXCJhY3RpdmVcIik7XG4gICAgfVxuICAgIHNldCBhY3RpdmUoc3RhdHVzOiBib29sZWFuKSB7XG4gICAgICAgIHN0YXR1cyA/IHRoaXMuY2xhc3NMaXN0LmFkZChcImFjdGl2ZVwiKSA6IHRoaXMuY2xhc3NMaXN0LnJlbW92ZShcImFjdGl2ZVwiKTtcbiAgICB9XG5cbiAgICAvLyBhZGRzIGNsYXNzIGBhY3RpdmVgIHRvIGFjdGl2ZSBidXR0b24gYW5kIHJlbW92ZXMgaXQgZnJvbSBhbGwgb3RoZXJzLlxuICAgIGFjdGl2YXRlRXhjbHVzaXZlKCk6IHZvaWQge1xuICAgICAgICBjb25zdCBidG5zOiBTeXN0b3JpU29ydEJ1dHRvbltdID0gQXJyYXkuZnJvbShcbiAgICAgICAgICAgIGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGwoXCJzeXMtc29ydC1idXR0b25cIiksXG4gICAgICAgICk7XG4gICAgICAgIGZvciAoY29uc3QgYnRuIG9mIGJ0bnMpIHtcbiAgICAgICAgICAgIGJ0bi5hY3RpdmUgPSBmYWxzZTtcbiAgICAgICAgfVxuICAgICAgICB0aGlzLmFjdGl2ZSA9IHRydWU7XG4gICAgfVxuXG4gICAgc29ydFByb2plY3RUaWxlcyh0b2dnbGVBc2M6IGJvb2xlYW4pOiB2b2lkIHtcbiAgICAgICAgLy8gc3RhcnRpbmcgd2l0aCB0b2dnbGluZyBzb3J0aW5nIG9yZGVyLCBtb3ZlIHRvIGJvdHRvbSB0byBleGNoYW5nZSB0cnVlL2ZhbHNlIGJlaGF2aW91clxuICAgICAgICBpZiAodG9nZ2xlQXNjKSB0aGlzLnRvZ2dsZUFzYygpO1xuICAgICAgICB0aGlzLmFjdGl2YXRlRXhjbHVzaXZlKCk7XG5cbiAgICAgICAgY29uc3QgcHJvamVjdFRpbGVzID0gQXJyYXkuZnJvbShcbiAgICAgICAgICAgIGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGw8U3lzdG9yaVByb2plY3RUaWxlPihcIi50aWxlXCIpLFxuICAgICAgICApO1xuXG4gICAgICAgIHByb2plY3RUaWxlcy5zb3J0KChhLCBiKSA9PiB7XG4gICAgICAgICAgICBzd2l0Y2ggKHRoaXMudHlwZSkge1xuICAgICAgICAgICAgICAgIGNhc2UgU29ydEJ1dHRvblR5cGUuaWQ6XG4gICAgICAgICAgICAgICAgICAgIGlmICh0aGlzLmFzYykge1xuICAgICAgICAgICAgICAgICAgICAgICAgcmV0dXJuIGIucGsgPCBhLnBrID8gLTEgOiAxO1xuICAgICAgICAgICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgICAgICAgICAgcmV0dXJuIGEucGsgPCBiLnBrID8gLTEgOiAxO1xuICAgICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgY2FzZSBTb3J0QnV0dG9uVHlwZS5uYW1lOlxuICAgICAgICAgICAgICAgICAgICBpZiAodGhpcy5hc2MpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIHJldHVybiBhLm5hbWUubG9jYWxlQ29tcGFyZShiLm5hbWUpO1xuICAgICAgICAgICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgICAgICAgICAgcmV0dXJuIGIubmFtZS5sb2NhbGVDb21wYXJlKGEubmFtZSk7XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICBjYXNlIFNvcnRCdXR0b25UeXBlLnBoYXNlOlxuICAgICAgICAgICAgICAgICAgICBpZiAodGhpcy5hc2MpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIHJldHVybiBQaGFzZU9yZGVyW2IucGhhc2VdIDw9IFBoYXNlT3JkZXJbYS5waGFzZV1cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICA/IC0xXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgOiAxO1xuICAgICAgICAgICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgICAgICAgICAgcmV0dXJuIFBoYXNlT3JkZXJbYS5waGFzZV0gPD0gUGhhc2VPcmRlcltiLnBoYXNlXVxuICAgICAgICAgICAgICAgICAgICAgICAgICAgID8gLTFcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICA6IDE7XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICBkZWZhdWx0OlxuICAgICAgICAgICAgICAgICAgICB0aHJvdyBuZXcgRXJyb3IoXG4gICAgICAgICAgICAgICAgICAgICAgICBgQ2FuJ3QgZmluZCBhIFNvcnRCdXR0b25UeXBlIHR5cGUgZm9yICR7dGhpcy50eXBlfS5gLFxuICAgICAgICAgICAgICAgICAgICApO1xuICAgICAgICAgICAgfVxuICAgICAgICB9KTtcblxuICAgICAgICBpZiAodGlsZUNvbnRhaW5lcikge1xuICAgICAgICAgICAgdGlsZUNvbnRhaW5lci5pbm5lckhUTUwgPSBcIlwiO1xuICAgICAgICAgICAgZm9yIChjb25zdCB0aWxlIG9mIHByb2plY3RUaWxlcykge1xuICAgICAgICAgICAgICAgIHRpbGVDb250YWluZXIuYXBwZW5kQ2hpbGQodGlsZSk7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cblxuICAgICAgICB0aGlzLnNhdmVTdGF0ZVRvTG9jYWxTdG9yYWdlKCk7XG4gICAgfVxuXG4gICAgc2F2ZVN0YXRlVG9Mb2NhbFN0b3JhZ2UoKTogdm9pZCB7XG4gICAgICAgIGxvY2FsU3RvcmFnZS5zZXRJdGVtKFxuICAgICAgICAgICAgXCJzdGF0ZS1TeXN0b3JpU29ydEJ1dHRvblwiLFxuICAgICAgICAgICAgSlNPTi5zdHJpbmdpZnkoe1xuICAgICAgICAgICAgICAgIHR5cGU6IHRoaXMudHlwZSxcbiAgICAgICAgICAgICAgICBhc2M6IHRoaXMuYXNjLFxuICAgICAgICAgICAgICAgIGFjdGl2ZTogdGhpcy5hY3RpdmUsXG4gICAgICAgICAgICB9KSxcbiAgICAgICAgKTtcbiAgICB9XG4gICAgX2xvYWRTdGF0ZUZyb21Mb2NhbFN0b3JhZ2UoKTogdm9pZCB7XG4gICAgICAgIGNvbnNvbGUubG9nKFxuICAgICAgICAgICAgYFN5c3RvcmlTb3J0QnV0dG9uIHR5cGU9PSR7dGhpcy50eXBlfSBhY3RpdmUgc3RhdGU9PSR7dGhpcy5hY3RpdmV9LmAsXG4gICAgICAgICAgICBgYmFja2dyb3VuZDogZnVjaHNpYTsgY29sb3I6ICMzZTNlM2VgLFxuICAgICAgICApO1xuICAgICAgICAvLyBjaGVjayBpZiBjdXN0b20gZWxlbWVudCBpcyBib3VuZCB0byBkb21cbiAgICAgICAgaWYgKHRoaXMuYWN0aXZlIHx8ICF0aGlzLmFjdGl2ZSkge1xuICAgICAgICAgICAgY29uc3Qgc29ydEpzb24gPSBsb2NhbFN0b3JhZ2UuZ2V0SXRlbShcInN0YXRlLVN5c3RvcmlTb3J0QnV0dG9uXCIpO1xuICAgICAgICAgICAgaWYgKHNvcnRKc29uKSB7XG4gICAgICAgICAgICAgICAgY29uc3Qgc3RhdGU6IFNvcnRCdXR0b25TdGF0ZSA9IEpTT04ucGFyc2Uoc29ydEpzb24pO1xuICAgICAgICAgICAgICAgIGNvbnNvbGUuaW5mbyhcbiAgICAgICAgICAgICAgICAgICAgYFN5c3RvcmlTb3J0QnV0dG9uIHR5cGU9PSR7dGhpcy50eXBlfSBsb2NhbFN0b3JhZ2UgYWN0aXZlIHN0YXRlPT0ke3N0YXRlLmFjdGl2ZX0uYCxcbiAgICAgICAgICAgICAgICApO1xuICAgICAgICAgICAgICAgIGlmICh0aGlzLnR5cGUgPT09IHN0YXRlLnR5cGUpIHtcbiAgICAgICAgICAgICAgICAgICAgdGhpcy5hc2MgPSBzdGF0ZS5hc2M7XG4gICAgICAgICAgICAgICAgICAgIHRoaXMuc29ydFByb2plY3RUaWxlcyhmYWxzZSk7XG4gICAgICAgICAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgICAgICAgICAgdGhpcy5hY3RpdmUgPSBmYWxzZTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICB9XG4gICAgY29ubmVjdGVkQ2FsbGJhY2soKTogdm9pZCB7XG4gICAgICAgIGNvbnNvbGUuaW5mbyhgU3lzdG9yaVNvcnRCdXR0b24gdHlwZT09JHt0aGlzLnR5cGV9IHdhcyBhdHRhY2hlZC5gKTtcbiAgICAgICAgdGhpcy5fbG9hZFN0YXRlRnJvbUxvY2FsU3RvcmFnZSgpO1xuICAgIH1cbn1cblxuZnVuY3Rpb24gc2F2ZVBoYXNlU3RhdGVUb0xvY2FsU3RvcmFnZSgpOiB2b2lkIHtcbiAgICBjb25zdCBidG5zOiBTeXN0b3JpUGhhc2VCdXR0b25bXSA9IEFycmF5LmZyb20oXG4gICAgICAgIGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGwoXCJzeXMtcGhhc2UtYnV0dG9uXCIpLFxuICAgICk7XG4gICAgY29uc3QgYnRuc1N0YXRlOiBQaGFzZUJ1dHRvblN0YXRlW10gPSBbXTtcbiAgICBmb3IgKGNvbnN0IGJ0biBvZiBidG5zKSB7XG4gICAgICAgIGJ0bnNTdGF0ZS5wdXNoKHsgcGhhc2U6IGJ0bi5waGFzZSwgaGlkZVBoYXNlOiBidG4uaGlkZVBoYXNlIH0pO1xuICAgIH1cbiAgICBsb2NhbFN0b3JhZ2Uuc2V0SXRlbShcInN0YXRlLVN5c3RvcmlQaGFzZUJ1dHRvblwiLCBKU09OLnN0cmluZ2lmeShidG5zU3RhdGUpKTtcbn1cblxuY2xhc3MgU3lzdG9yaVBoYXNlQnV0dG9uIGV4dGVuZHMgSFRNTEVsZW1lbnQge1xuICAgIGNvbnN0cnVjdG9yKCkge1xuICAgICAgICBzdXBlcigpO1xuICAgICAgICB0aGlzLmFkZEV2ZW50TGlzdGVuZXIoXCJjbGlja1wiLCAoKSA9PiB0aGlzLmZpbHRlclByb2plY3RUaWxlcyh0cnVlKSk7XG4gICAgfVxuXG4gICAgZ2V0IHBoYXNlKCk6IHN0cmluZyB7XG4gICAgICAgIHJldHVybiB0aGlzLmRhdGFzZXQucGhhc2UhO1xuICAgIH1cbiAgICBzZXQgcGhhc2UocGhhc2U6IHN0cmluZykge1xuICAgICAgICB0aGlzLmRhdGFzZXQucGhhc2UgPSBwaGFzZTtcbiAgICB9XG5cbiAgICAvLyBoaWRlUGhhc2UgPT09IGhpZGRlblxuICAgIGdldCBoaWRlUGhhc2UoKTogYm9vbGVhbiB7XG4gICAgICAgIHJldHVybiB0aGlzLmNsYXNzTGlzdC5jb250YWlucyhcImhpZGUtcGhhc2VcIik7XG4gICAgfVxuICAgIHNldCBoaWRlUGhhc2UoaGlkZTogYm9vbGVhbikge1xuICAgICAgICBoaWRlXG4gICAgICAgICAgICA/IHRoaXMuY2xhc3NMaXN0LmFkZChcImhpZGUtcGhhc2VcIilcbiAgICAgICAgICAgIDogdGhpcy5jbGFzc0xpc3QucmVtb3ZlKFwiaGlkZS1waGFzZVwiKTtcbiAgICB9XG5cbiAgICB0b2dnbGVQcm9qZWN0VGlsZXMoaGlkZTogYm9vbGVhbik6IHZvaWQge1xuICAgICAgICBjb25zdCBwcm9qZWN0VGlsZXM6IFN5c3RvcmlQcm9qZWN0VGlsZVtdID0gQXJyYXkuZnJvbShcbiAgICAgICAgICAgIGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGwoXG4gICAgICAgICAgICAgICAgYHN5cy1wcm9qZWN0LXRpbGVbZGF0YS1waGFzZT0ke3RoaXMucGhhc2V9XWAsXG4gICAgICAgICAgICApLFxuICAgICAgICApO1xuICAgICAgICBmb3IgKGNvbnN0IHRpbGUgb2YgcHJvamVjdFRpbGVzKSB7XG4gICAgICAgICAgICB0aWxlLmhpZGUoaGlkZSk7XG4gICAgICAgIH1cbiAgICAgICAgc2F2ZVBoYXNlU3RhdGVUb0xvY2FsU3RvcmFnZSgpO1xuICAgIH1cblxuICAgIGZpbHRlclByb2plY3RUaWxlcyh0b2dnbGU6IGJvb2xlYW4pOiB2b2lkIHtcbiAgICAgICAgaWYgKHRvZ2dsZSkgdGhpcy5oaWRlUGhhc2UgPSAhdGhpcy5oaWRlUGhhc2U7XG4gICAgICAgIHRoaXMuaGlkZVBoYXNlXG4gICAgICAgICAgICA/IHRoaXMudG9nZ2xlUHJvamVjdFRpbGVzKHRydWUpXG4gICAgICAgICAgICA6IHRoaXMudG9nZ2xlUHJvamVjdFRpbGVzKGZhbHNlKTtcbiAgICB9XG59XG5cbmNsYXNzIFN5c3RvcmlTZWFyY2hFbGVtZW50IGV4dGVuZHMgSFRNTEVsZW1lbnQge1xuICAgIC8vIFRoaXMgY3VzdG9tIGVsZW1lbnQgaXMgZm9yIGNvbXBvc2luZyB0aGUgdHdvIGNoaWxkTm9kZXMuXG4gICAgY29uc3RydWN0b3IoKSB7XG4gICAgICAgIHN1cGVyKCk7XG4gICAgfVxufVxuXG5jbGFzcyBTeXN0b3JpU2VhcmNoSW5wdXQgZXh0ZW5kcyBIVE1MSW5wdXRFbGVtZW50IHtcbiAgICBjb25zdHJ1Y3RvcigpIHtcbiAgICAgICAgc3VwZXIoKTtcbiAgICAgICAgdGhpcy5hZGRFdmVudExpc3RlbmVyKFwia2V5dXBcIiwgKCkgPT4gdGhpcy5hcGlTZWFyY2hQcm9qZWN0cygpKTtcbiAgICB9XG5cbiAgICBhcGlTZWFyY2hQcm9qZWN0cygpOiBudW1iZXJbXSB7XG4gICAgICAgIGNvbnN0IHByb2plY3RzID0gW10gYXMgbnVtYmVyW107XG4gICAgICAgIHByb2plY3RzLnB1c2goMTEpO1xuICAgICAgICBwcm9qZWN0cy5wdXNoKDIzKTtcbiAgICAgICAgcmV0dXJuIHByb2plY3RzO1xuICAgIH1cbn1cblxuZnVuY3Rpb24gbG9hZExvY2FsU3RvcmFnZSgpOiB2b2lkIHtcbiAgICAvLyBjb25zdCBzb3J0SnNvbiA9IGxvY2FsU3RvcmFnZS5nZXRJdGVtKFwic3RhdGUtU3lzdG9yaVNvcnRCdXR0b25cIik7XG4gICAgY29uc3QgcGhhc2VKc29uID0gbG9jYWxTdG9yYWdlLmdldEl0ZW0oXCJzdGF0ZS1TeXN0b3JpUGhhc2VCdXR0b25cIik7XG4gICAgLy8gaWYgKHNvcnRKc29uKSB7XG4gICAgLy8gICAgIGNvbnN0IHN0YXRlOiBTb3J0QnV0dG9uU3RhdGUgPSBKU09OLnBhcnNlKHNvcnRKc29uKTtcbiAgICAvLyAgICAgY29uc3QgYnRuczogU3lzdG9yaVNvcnRCdXR0b25bXSA9IEFycmF5LmZyb20oXG4gICAgLy8gICAgICAgICBkb2N1bWVudC5xdWVyeVNlbGVjdG9yQWxsKFwic3lzLXNvcnQtYnV0dG9uXCIpLFxuICAgIC8vICAgICApO1xuICAgIC8vICAgICBmb3IgKGNvbnN0IGJ0biBvZiBidG5zKSB7XG4gICAgLy8gICAgICAgICBpZiAoYnRuLnR5cGUgPT09IHN0YXRlLnR5cGUpIHtcbiAgICAvLyAgICAgICAgICAgICBidG4uYXNjID0gc3RhdGUuYXNjO1xuICAgIC8vICAgICAgICAgICAgIGJ0bi5zb3J0UHJvamVjdFRpbGVzKGZhbHNlKTtcbiAgICAvLyAgICAgICAgIH0gZWxzZSB7XG4gICAgLy8gICAgICAgICAgICAgYnRuLmFjdGl2ZSA9IGZhbHNlO1xuICAgIC8vICAgICAgICAgfVxuICAgIC8vICAgICB9XG4gICAgLy8gfVxuICAgIGlmIChwaGFzZUpzb24pIHtcbiAgICAgICAgY29uc3Qgc3RhdGU6IFBoYXNlQnV0dG9uU3RhdGVbXSA9IEpTT04ucGFyc2UocGhhc2VKc29uKTtcbiAgICAgICAgY29uc3QgYnRuczogU3lzdG9yaVBoYXNlQnV0dG9uW10gPSBBcnJheS5mcm9tKFxuICAgICAgICAgICAgZG9jdW1lbnQucXVlcnlTZWxlY3RvckFsbChcInN5cy1waGFzZS1idXR0b25cIiksXG4gICAgICAgICk7XG4gICAgICAgIGZvciAoY29uc3QgcCBvZiBzdGF0ZSkge1xuICAgICAgICAgICAgaWYgKHAuaGlkZVBoYXNlKSB7XG4gICAgICAgICAgICAgICAgZm9yIChjb25zdCBidG4gb2YgYnRucykge1xuICAgICAgICAgICAgICAgICAgICBpZiAoYnRuLnBoYXNlID09PSBwLnBoYXNlKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICBidG4uaGlkZVBoYXNlID0gcC5oaWRlUGhhc2U7XG4gICAgICAgICAgICAgICAgICAgICAgICBidG4uZmlsdGVyUHJvamVjdFRpbGVzKGZhbHNlKTtcbiAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgIH1cbn1cblxuY3VzdG9tRWxlbWVudHMuZGVmaW5lKFwic3lzLXNlYXJjaC1pbnB1dFwiLCBTeXN0b3JpU2VhcmNoSW5wdXQsIHtcbiAgICBleHRlbmRzOiBcImlucHV0XCIsXG59KTtcbmN1c3RvbUVsZW1lbnRzLmRlZmluZShcInN5cy1zZWFyY2gtZWxlbWVudFwiLCBTeXN0b3JpU2VhcmNoRWxlbWVudCk7XG5jdXN0b21FbGVtZW50cy5kZWZpbmUoXCJzeXMtcGhhc2UtYnV0dG9uXCIsIFN5c3RvcmlQaGFzZUJ1dHRvbik7XG5jdXN0b21FbGVtZW50cy5kZWZpbmUoXCJzeXMtc29ydC1idXR0b25cIiwgU3lzdG9yaVNvcnRCdXR0b24pO1xuY3VzdG9tRWxlbWVudHMuZGVmaW5lKFwic3lzLXByb2plY3QtdGlsZVwiLCBTeXN0b3JpUHJvamVjdFRpbGUpO1xuXG5sb2FkTG9jYWxTdG9yYWdlKCk7XG5pZiAoZmlsdGVyQmFyKSB7XG4gICAgZmlsdGVyQmFyLmNsYXNzTGlzdC5yZW1vdmUoXCJoaWRkZW5cIik7XG59XG5pZiAodGlsZUNvbnRhaW5lcikge1xuICAgIHRpbGVDb250YWluZXIuY2xhc3NMaXN0LnJlbW92ZShcImhpZGRlblwiKTtcbn1cbiJdLCJzb3VyY2VSb290IjoiIn0=