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

function getCookie(query) {
    const cookies = document.cookie.split(";");
    for (const cookie of cookies) {
        const [name, value] = cookie.split("=");
        if (name === query) {
            return value;
        }
    }
    return "";
}
const filterBar = document.querySelector(".filter-bar");
const tileContainer = document.querySelector(".tile-container");
const csrfToken = getCookie("csrftoken");
const headers = new Headers({
    "Content-Type": "application/json",
    Accept: "application/json",
    "X-CSRFToken": csrfToken,
});
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
        return this.classList.contains("hidden");
    }
    hide(hide) {
        hide ? this.classList.add("hidden") : this.classList.remove("hidden");
    }
}
class SystoriSortButton extends HTMLElement {
    constructor() {
        super();
        this.addEventListener("click", () => this.clickHandler());
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
        this.classList.toggle("active", status);
    }
    clickHandler() {
        this.toggleAsc();
        this.activateExclusive();
        this.sortProjectTiles();
        this._saveStateToLocalStorage();
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
                    // ToDo: switch x.dataset.name! back to x.name if it works with _loadStateFromLocalStorage
                    if (this.asc) {
                        return a.dataset.name.localeCompare(b.dataset.name);
                    }
                    else {
                        return b.dataset.name.localeCompare(a.dataset.name);
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
        this._saveStateToLocalStorage();
    }
    _saveStateToLocalStorage() {
        localStorage.setItem("state-SystoriSortButton", JSON.stringify({
            type: this.type,
            asc: this.asc,
        }));
    }
    _loadStateFromLocalStorage() {
        if (this.active || !this.active) {
            const sortJson = localStorage.getItem("state-SystoriSortButton");
            if (sortJson) {
                const state = JSON.parse(sortJson);
                if (this.type === state.type) {
                    this.asc = state.asc;
                    this.active = true;
                    this.sortProjectTiles();
                }
                else {
                    delete this.dataset.active;
                    this.active = false;
                }
            }
        }
    }
    connectedCallback() {
        this._loadStateFromLocalStorage();
    }
}
class SystoriPhaseButton extends HTMLElement {
    constructor() {
        super();
        this.addEventListener("click", () => this.clickHandler());
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
    toggleProjectTiles(status) {
        const projectTiles = Array.from(document.querySelectorAll(`sys-project-tile[data-phase=${this.phase}]`));
        for (const tile of projectTiles) {
            tile.hide(status);
        }
    }
    clickHandler() {
        this.hidePhase = !this.hidePhase;
        this.filterProjectTiles();
        this._saveStateToLocalStorage();
    }
    filterProjectTiles() {
        this.hidePhase
            ? this.toggleProjectTiles(true)
            : this.toggleProjectTiles(false);
    }
    _saveStateToLocalStorage() {
        localStorage.setItem(`state-SystoriPhaseButton-${this.phase}`, JSON.stringify({
            hidePhase: this.hidePhase,
        }));
    }
    _loadStateFromLocalStorage() {
        const stateJson = localStorage.getItem(`state-SystoriPhaseButton-${this.phase}`);
        if (stateJson) {
            const state = JSON.parse(stateJson);
            this.hidePhase = state.hidePhase;
            this.filterProjectTiles();
        }
    }
    connectedCallback() {
        this._loadStateFromLocalStorage();
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
        this.addEventListener("keyup", () => this.clickHandler());
    }
    filterProjectTiles(searchResultPks) {
        const projectPks = this.getAllLocalProjectPks();
        // all projects except the found projects
        const difference = projectPks.filter(pk => !searchResultPks.includes(pk));
        for (const pk of difference) {
            const tile = document.querySelector(`sys-project-tile[data-pk="${pk}"]`);
            if (tile)
                tile.hide(true);
        }
    }
    showAllProjects() {
        const phaseBtns = new Map();
        Array.from(document.querySelectorAll("sys-phase-button")).map(tile => phaseBtns.set(tile.phase, tile.hidePhase));
        const projectPks = this.getAllLocalProjectPks();
        for (const pk of projectPks) {
            const tile = document.querySelector(`sys-project-tile[data-pk="${pk}"]`);
            if (tile && !phaseBtns.get(tile.phase))
                tile.hide(false);
        }
        const cancelButton = document.querySelector("sys-search-cancel-button");
        cancelButton.visible = false;
    }
    getAllLocalProjectPks() {
        return Array.from(document.querySelectorAll(`sys-project-tile`)).map(tile => {
            return tile.pk;
        });
    }
    apiSearchProjects() {
        localStorage.setItem("sys-project-search-input", this.value);
        fetch("/api/project/search/", {
            method: "put",
            credentials: "same-origin",
            headers: headers,
            body: JSON.stringify({ query: this.value }),
        })
            .then(response => response.json())
            .then(body => {
            this.filterProjectTiles(body.projects);
        });
    }
    processQuery() {
        const cancelButton = document.querySelector("sys-search-cancel-button");
        cancelButton.visible = true;
        this.apiSearchProjects();
    }
    delayedClickHandler() {
        this.value == "" ? this.showAllProjects() : this.processQuery();
    }
    clickHandler() {
        if (this.timeout)
            clearTimeout(this.timeout);
        this.timeout = setTimeout(() => {
            this.value == "" ? this.showAllProjects() : this.processQuery();
        }, 300);
    }
}
class SystoriSearchCancelButton extends HTMLElement {
    constructor() {
        super();
        this.addEventListener("click", () => this.clickHandler());
    }
    get visible() {
        return this.classList.contains("visible");
    }
    set visible(status) {
        this.classList.toggle("visible", status);
    }
    clickHandler() {
        if (this.parentElement) {
            const input = this.parentElement.querySelector('input[is="sys-search-input"]');
            if (input) {
                input.value = "";
                input.showAllProjects();
                this.visible = false;
            }
        }
    }
}
customElements.define("sys-project-tile", SystoriProjectTile);
customElements.define("sys-search-input", SystoriSearchInput, {
    extends: "input",
});
customElements.define("sys-search-element", SystoriSearchElement);
customElements.define("sys-search-cancel-button", SystoriSearchCancelButton);
customElements.define("sys-phase-button", SystoriPhaseButton);
customElements.define("sys-sort-button", SystoriSortButton);
// loadLocalStorage();
if (filterBar) {
    filterBar.classList.remove("hidden");
}
if (tileContainer) {
    tileContainer.classList.remove("hidden");
}


/***/ })

/******/ });
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8vd2VicGFjay9ib290c3RyYXAiLCJ3ZWJwYWNrOi8vLy4vc3JjL3Byb2plY3RfbGlzdC50cyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiO1FBQUE7UUFDQTs7UUFFQTtRQUNBOztRQUVBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBOztRQUVBO1FBQ0E7O1FBRUE7UUFDQTs7UUFFQTtRQUNBO1FBQ0E7OztRQUdBO1FBQ0E7O1FBRUE7UUFDQTs7UUFFQTtRQUNBO1FBQ0E7UUFDQSwwQ0FBMEMsZ0NBQWdDO1FBQzFFO1FBQ0E7O1FBRUE7UUFDQTtRQUNBO1FBQ0Esd0RBQXdELGtCQUFrQjtRQUMxRTtRQUNBLGlEQUFpRCxjQUFjO1FBQy9EOztRQUVBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQSx5Q0FBeUMsaUNBQWlDO1FBQzFFLGdIQUFnSCxtQkFBbUIsRUFBRTtRQUNySTtRQUNBOztRQUVBO1FBQ0E7UUFDQTtRQUNBLDJCQUEyQiwwQkFBMEIsRUFBRTtRQUN2RCxpQ0FBaUMsZUFBZTtRQUNoRDtRQUNBO1FBQ0E7O1FBRUE7UUFDQSxzREFBc0QsK0RBQStEOztRQUVySDtRQUNBOzs7UUFHQTtRQUNBOzs7Ozs7Ozs7Ozs7OztBQ2xGQSxTQUFTLFNBQVMsQ0FBQyxLQUFhO0lBQzVCLE1BQU0sT0FBTyxHQUFHLFFBQVEsQ0FBQyxNQUFNLENBQUMsS0FBSyxDQUFDLEdBQUcsQ0FBQyxDQUFDO0lBQzNDLEtBQUssTUFBTSxNQUFNLElBQUksT0FBTyxFQUFFO1FBQzFCLE1BQU0sQ0FBQyxJQUFJLEVBQUUsS0FBSyxDQUFDLEdBQUcsTUFBTSxDQUFDLEtBQUssQ0FBQyxHQUFHLENBQUMsQ0FBQztRQUN4QyxJQUFJLElBQUksS0FBSyxLQUFLLEVBQUU7WUFDaEIsT0FBTyxLQUFLLENBQUM7U0FDaEI7S0FDSjtJQUNELE9BQU8sRUFBRSxDQUFDO0FBQ2QsQ0FB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QUFFLGtCQUFrQixDQUFDLENBQUM7QUFDOUQsY0FBYyxDQUFDLE1BQU0sQ0FBQyxrQkFBa0IsRUFBRSxrQkFBa0IsRUFBRTtJQUMxRCxPQUFPLEVBQUUsT0FBTztDQUNuQixDQUFDLENBQUM7QUFDSCxjQUFjLENBQUMsTUFBTSxDQUFDLG9CQUFvQixFQUFFLG9CQUFvQixDQUFDLENBQUM7QUFDbEUsY0FBYyxDQUFDLE1BQU0sQ0FBQywwQkFBMEIsRUFBRSx5QkFBeUIsQ0FBQyxDQUFDO0FBQzdFLGNBQWMsQ0FBQyxNQUFNLENBQUMsa0JBQWtCLEVBQUUsa0JBQWtCLENBQUMsQ0FBQztBQUM5RCxjQUFjLENBQUMsTUFBTSxDQUFDLGlCQUFpQixFQUFFLGlCQUFpQixDQUFDLENBQUM7QUFFNUQsc0JBQXNCO0FBQ3RCLElBQUksU0FBUyxFQUFFO0lBQ1gsU0FBUyxDQUFDLFNBQVMsQ0FBQyxNQUFNLENBQUMsUUFBUSxDQUFDLENBQUM7Q0FDeEM7QUFDRCxJQUFJLGFBQWEsRUFBRTtJQUNmLGFBQWEsQ0FBQyxTQUFTLENBQUMsTUFBTSxDQUFDLFFBQVEsQ0FBQyxDQUFDO0NBQzVDIiwiZmlsZSI6InByb2plY3RfbGlzdC5qcyIsInNvdXJjZXNDb250ZW50IjpbIiBcdC8vIFRoZSBtb2R1bGUgY2FjaGVcbiBcdHZhciBpbnN0YWxsZWRNb2R1bGVzID0ge307XG5cbiBcdC8vIFRoZSByZXF1aXJlIGZ1bmN0aW9uXG4gXHRmdW5jdGlvbiBfX3dlYnBhY2tfcmVxdWlyZV9fKG1vZHVsZUlkKSB7XG5cbiBcdFx0Ly8gQ2hlY2sgaWYgbW9kdWxlIGlzIGluIGNhY2hlXG4gXHRcdGlmKGluc3RhbGxlZE1vZHVsZXNbbW9kdWxlSWRdKSB7XG4gXHRcdFx0cmV0dXJuIGluc3RhbGxlZE1vZHVsZXNbbW9kdWxlSWRdLmV4cG9ydHM7XG4gXHRcdH1cbiBcdFx0Ly8gQ3JlYXRlIGEgbmV3IG1vZHVsZSAoYW5kIHB1dCBpdCBpbnRvIHRoZSBjYWNoZSlcbiBcdFx0dmFyIG1vZHVsZSA9IGluc3RhbGxlZE1vZHVsZXNbbW9kdWxlSWRdID0ge1xuIFx0XHRcdGk6IG1vZHVsZUlkLFxuIFx0XHRcdGw6IGZhbHNlLFxuIFx0XHRcdGV4cG9ydHM6IHt9XG4gXHRcdH07XG5cbiBcdFx0Ly8gRXhlY3V0ZSB0aGUgbW9kdWxlIGZ1bmN0aW9uXG4gXHRcdG1vZHVsZXNbbW9kdWxlSWRdLmNhbGwobW9kdWxlLmV4cG9ydHMsIG1vZHVsZSwgbW9kdWxlLmV4cG9ydHMsIF9fd2VicGFja19yZXF1aXJlX18pO1xuXG4gXHRcdC8vIEZsYWcgdGhlIG1vZHVsZSBhcyBsb2FkZWRcbiBcdFx0bW9kdWxlLmwgPSB0cnVlO1xuXG4gXHRcdC8vIFJldHVybiB0aGUgZXhwb3J0cyBvZiB0aGUgbW9kdWxlXG4gXHRcdHJldHVybiBtb2R1bGUuZXhwb3J0cztcbiBcdH1cblxuXG4gXHQvLyBleHBvc2UgdGhlIG1vZHVsZXMgb2JqZWN0IChfX3dlYnBhY2tfbW9kdWxlc19fKVxuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy5tID0gbW9kdWxlcztcblxuIFx0Ly8gZXhwb3NlIHRoZSBtb2R1bGUgY2FjaGVcbiBcdF9fd2VicGFja19yZXF1aXJlX18uYyA9IGluc3RhbGxlZE1vZHVsZXM7XG5cbiBcdC8vIGRlZmluZSBnZXR0ZXIgZnVuY3Rpb24gZm9yIGhhcm1vbnkgZXhwb3J0c1xuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy5kID0gZnVuY3Rpb24oZXhwb3J0cywgbmFtZSwgZ2V0dGVyKSB7XG4gXHRcdGlmKCFfX3dlYnBhY2tfcmVxdWlyZV9fLm8oZXhwb3J0cywgbmFtZSkpIHtcbiBcdFx0XHRPYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgbmFtZSwgeyBlbnVtZXJhYmxlOiB0cnVlLCBnZXQ6IGdldHRlciB9KTtcbiBcdFx0fVxuIFx0fTtcblxuIFx0Ly8gZGVmaW5lIF9fZXNNb2R1bGUgb24gZXhwb3J0c1xuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy5yID0gZnVuY3Rpb24oZXhwb3J0cykge1xuIFx0XHRpZih0eXBlb2YgU3ltYm9sICE9PSAndW5kZWZpbmVkJyAmJiBTeW1ib2wudG9TdHJpbmdUYWcpIHtcbiBcdFx0XHRPYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgU3ltYm9sLnRvU3RyaW5nVGFnLCB7IHZhbHVlOiAnTW9kdWxlJyB9KTtcbiBcdFx0fVxuIFx0XHRPYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgJ19fZXNNb2R1bGUnLCB7IHZhbHVlOiB0cnVlIH0pO1xuIFx0fTtcblxuIFx0Ly8gY3JlYXRlIGEgZmFrZSBuYW1lc3BhY2Ugb2JqZWN0XG4gXHQvLyBtb2RlICYgMTogdmFsdWUgaXMgYSBtb2R1bGUgaWQsIHJlcXVpcmUgaXRcbiBcdC8vIG1vZGUgJiAyOiBtZXJnZSBhbGwgcHJvcGVydGllcyBvZiB2YWx1ZSBpbnRvIHRoZSBuc1xuIFx0Ly8gbW9kZSAmIDQ6IHJldHVybiB2YWx1ZSB3aGVuIGFscmVhZHkgbnMgb2JqZWN0XG4gXHQvLyBtb2RlICYgOHwxOiBiZWhhdmUgbGlrZSByZXF1aXJlXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLnQgPSBmdW5jdGlvbih2YWx1ZSwgbW9kZSkge1xuIFx0XHRpZihtb2RlICYgMSkgdmFsdWUgPSBfX3dlYnBhY2tfcmVxdWlyZV9fKHZhbHVlKTtcbiBcdFx0aWYobW9kZSAmIDgpIHJldHVybiB2YWx1ZTtcbiBcdFx0aWYoKG1vZGUgJiA0KSAmJiB0eXBlb2YgdmFsdWUgPT09ICdvYmplY3QnICYmIHZhbHVlICYmIHZhbHVlLl9fZXNNb2R1bGUpIHJldHVybiB2YWx1ZTtcbiBcdFx0dmFyIG5zID0gT2JqZWN0LmNyZWF0ZShudWxsKTtcbiBcdFx0X193ZWJwYWNrX3JlcXVpcmVfXy5yKG5zKTtcbiBcdFx0T2JqZWN0LmRlZmluZVByb3BlcnR5KG5zLCAnZGVmYXVsdCcsIHsgZW51bWVyYWJsZTogdHJ1ZSwgdmFsdWU6IHZhbHVlIH0pO1xuIFx0XHRpZihtb2RlICYgMiAmJiB0eXBlb2YgdmFsdWUgIT0gJ3N0cmluZycpIGZvcih2YXIga2V5IGluIHZhbHVlKSBfX3dlYnBhY2tfcmVxdWlyZV9fLmQobnMsIGtleSwgZnVuY3Rpb24oa2V5KSB7IHJldHVybiB2YWx1ZVtrZXldOyB9LmJpbmQobnVsbCwga2V5KSk7XG4gXHRcdHJldHVybiBucztcbiBcdH07XG5cbiBcdC8vIGdldERlZmF1bHRFeHBvcnQgZnVuY3Rpb24gZm9yIGNvbXBhdGliaWxpdHkgd2l0aCBub24taGFybW9ueSBtb2R1bGVzXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLm4gPSBmdW5jdGlvbihtb2R1bGUpIHtcbiBcdFx0dmFyIGdldHRlciA9IG1vZHVsZSAmJiBtb2R1bGUuX19lc01vZHVsZSA/XG4gXHRcdFx0ZnVuY3Rpb24gZ2V0RGVmYXVsdCgpIHsgcmV0dXJuIG1vZHVsZVsnZGVmYXVsdCddOyB9IDpcbiBcdFx0XHRmdW5jdGlvbiBnZXRNb2R1bGVFeHBvcnRzKCkgeyByZXR1cm4gbW9kdWxlOyB9O1xuIFx0XHRfX3dlYnBhY2tfcmVxdWlyZV9fLmQoZ2V0dGVyLCAnYScsIGdldHRlcik7XG4gXHRcdHJldHVybiBnZXR0ZXI7XG4gXHR9O1xuXG4gXHQvLyBPYmplY3QucHJvdG90eXBlLmhhc093blByb3BlcnR5LmNhbGxcbiBcdF9fd2VicGFja19yZXF1aXJlX18ubyA9IGZ1bmN0aW9uKG9iamVjdCwgcHJvcGVydHkpIHsgcmV0dXJuIE9iamVjdC5wcm90b3R5cGUuaGFzT3duUHJvcGVydHkuY2FsbChvYmplY3QsIHByb3BlcnR5KTsgfTtcblxuIFx0Ly8gX193ZWJwYWNrX3B1YmxpY19wYXRoX19cbiBcdF9fd2VicGFja19yZXF1aXJlX18ucCA9IFwiXCI7XG5cblxuIFx0Ly8gTG9hZCBlbnRyeSBtb2R1bGUgYW5kIHJldHVybiBleHBvcnRzXG4gXHRyZXR1cm4gX193ZWJwYWNrX3JlcXVpcmVfXyhfX3dlYnBhY2tfcmVxdWlyZV9fLnMgPSBcIi4vc3JjL3Byb2plY3RfbGlzdC50c1wiKTtcbiIsImZ1bmN0aW9uIGdldENvb2tpZShxdWVyeTogc3RyaW5nKTogc3RyaW5nIHtcbiAgICBjb25zdCBjb29raWVzID0gZG9jdW1lbnQuY29va2llLnNwbGl0KFwiO1wiKTtcbiAgICBmb3IgKGNvbnN0IGNvb2tpZSBvZiBjb29raWVzKSB7XG4gICAgICAgIGNvbnN0IFtuYW1lLCB2YWx1ZV0gPSBjb29raWUuc3BsaXQoXCI9XCIpO1xuICAgICAgICBpZiAobmFtZSA9PT0gcXVlcnkpIHtcbiAgICAgICAgICAgIHJldHVybiB2YWx1ZTtcbiAgICAgICAgfVxuICAgIH1cbiAgICByZXR1cm4gXCJcIjtcbn1cbmNvbnN0IGZpbHRlckJhciA9IGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3IoXCIuZmlsdGVyLWJhclwiKTtcbmNvbnN0IHRpbGVDb250YWluZXIgPSBkb2N1bWVudC5xdWVyeVNlbGVjdG9yKFwiLnRpbGUtY29udGFpbmVyXCIpO1xuY29uc3QgY3NyZlRva2VuID0gZ2V0Q29va2llKFwiY3NyZnRva2VuXCIpO1xuY29uc3QgaGVhZGVycyA9IG5ldyBIZWFkZXJzKHtcbiAgICBcIkNvbnRlbnQtVHlwZVwiOiBcImFwcGxpY2F0aW9uL2pzb25cIixcbiAgICBBY2NlcHQ6IFwiYXBwbGljYXRpb24vanNvblwiLFxuICAgIFwiWC1DU1JGVG9rZW5cIjogY3NyZlRva2VuLFxufSk7XG5lbnVtIFBoYXNlT3JkZXIge1xuICAgIHByb3NwZWN0aXZlLFxuICAgIHRlbmRlcmluZyxcbiAgICBwbGFubmluZyxcbiAgICBleGVjdXRpbmcsXG4gICAgc2V0dGxlbWVudCxcbiAgICB3YXJyYW50eSxcbiAgICBmaW5pc2hlZCxcbn1cbmVudW0gU29ydEJ1dHRvblR5cGUge1xuICAgIGlkID0gXCJpZFwiLFxuICAgIG5hbWUgPSBcIm5hbWVcIixcbiAgICBwaGFzZSA9IFwicGhhc2VcIixcbn1cblxuaW50ZXJmYWNlIFNvcnRCdXR0b25TdGF0ZSB7XG4gICAgdHlwZTogU29ydEJ1dHRvblR5cGU7XG4gICAgYXNjOiBib29sZWFuO1xufVxuXG5jbGFzcyBTeXN0b3JpUHJvamVjdFRpbGUgZXh0ZW5kcyBIVE1MRWxlbWVudCB7XG4gICAgY29uc3RydWN0b3IoKSB7XG4gICAgICAgIHN1cGVyKCk7XG4gICAgfVxuICAgIGdldCBwaygpOiBudW1iZXIge1xuICAgICAgICByZXR1cm4gcGFyc2VJbnQodGhpcy5kYXRhc2V0LnBrISk7XG4gICAgfVxuICAgIGdldCBuYW1lKCk6IHN0cmluZyB7XG4gICAgICAgIHJldHVybiB0aGlzLmRhdGFzZXQubmFtZSE7XG4gICAgfVxuICAgIGdldCBwaGFzZSgpOiBQaGFzZU9yZGVyIHtcbiAgICAgICAgcmV0dXJuICh0aGlzLmRhdGFzZXQucGhhc2UgfHwgUGhhc2VPcmRlci5wcm9zcGVjdGl2ZSkgYXMgUGhhc2VPcmRlcjtcbiAgICB9XG4gICAgZ2V0IGhpZGRlbigpOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuY2xhc3NMaXN0LmNvbnRhaW5zKFwiaGlkZGVuXCIpO1xuICAgIH1cbiAgICBoaWRlKGhpZGU6IGJvb2xlYW4pOiB2b2lkIHtcbiAgICAgICAgaGlkZSA/IHRoaXMuY2xhc3NMaXN0LmFkZChcImhpZGRlblwiKSA6IHRoaXMuY2xhc3NMaXN0LnJlbW92ZShcImhpZGRlblwiKTtcbiAgICB9XG59XG5cbmNsYXNzIFN5c3RvcmlTb3J0QnV0dG9uIGV4dGVuZHMgSFRNTEVsZW1lbnQge1xuICAgIGNvbnN0cnVjdG9yKCkge1xuICAgICAgICBzdXBlcigpO1xuICAgICAgICB0aGlzLmFkZEV2ZW50TGlzdGVuZXIoXCJjbGlja1wiLCAoKSA9PiB0aGlzLmNsaWNrSGFuZGxlcigpKTtcbiAgICB9XG4gICAgZ2V0IHR5cGUoKTogU29ydEJ1dHRvblR5cGUge1xuICAgICAgICBzd2l0Y2ggKHRoaXMuZGF0YXNldC50eXBlKSB7XG4gICAgICAgICAgICBjYXNlIFwiaWRcIjpcbiAgICAgICAgICAgICAgICByZXR1cm4gU29ydEJ1dHRvblR5cGUuaWQ7XG4gICAgICAgICAgICBjYXNlIFwibmFtZVwiOlxuICAgICAgICAgICAgICAgIHJldHVybiBTb3J0QnV0dG9uVHlwZS5uYW1lO1xuICAgICAgICAgICAgY2FzZSBcInBoYXNlXCI6XG4gICAgICAgICAgICAgICAgcmV0dXJuIFNvcnRCdXR0b25UeXBlLnBoYXNlO1xuICAgICAgICAgICAgZGVmYXVsdDpcbiAgICAgICAgICAgICAgICB0aHJvdyBFcnJvcihcIkNvdWxkbid0IGNhdGNoIFNvcnRCdXR0b25UeXBlLlwiKTtcbiAgICAgICAgfVxuICAgIH1cbiAgICBzZXQgdHlwZSh0eXBlOiBTb3J0QnV0dG9uVHlwZSkge1xuICAgICAgICB0aGlzLmRhdGFzZXQudHlwZSA9IFNvcnRCdXR0b25UeXBlW3R5cGVdO1xuICAgIH1cblxuICAgIC8vIEFTQy9ERVNDIHNvcnRpbmcgb3JkZXJcbiAgICBnZXQgYXNjKCk6IGJvb2xlYW4ge1xuICAgICAgICByZXR1cm4gdGhpcy5kYXRhc2V0LmFzYyA9PSBcInRydWVcIjtcbiAgICB9XG4gICAgc2V0IGFzYyhhc2M6IGJvb2xlYW4pIHtcbiAgICAgICAgYXNjID8gKHRoaXMuZGF0YXNldC5hc2MgPSBcInRydWVcIikgOiAodGhpcy5kYXRhc2V0LmFzYyA9IFwiZmFsc2VcIik7XG4gICAgfVxuICAgIHRvZ2dsZUFzYygpOiB2b2lkIHtcbiAgICAgICAgdGhpcy5hc2MgPSAhdGhpcy5hc2M7XG4gICAgfVxuXG4gICAgZ2V0IGFjdGl2ZSgpOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuY2xhc3NMaXN0LmNvbnRhaW5zKFwiYWN0aXZlXCIpO1xuICAgIH1cbiAgICBzZXQgYWN0aXZlKHN0YXR1czogYm9vbGVhbikge1xuICAgICAgICB0aGlzLmNsYXNzTGlzdC50b2dnbGUoXCJhY3RpdmVcIiwgc3RhdHVzKTtcbiAgICB9XG5cbiAgICBjbGlja0hhbmRsZXIoKTogdm9pZCB7XG4gICAgICAgIHRoaXMudG9nZ2xlQXNjKCk7XG4gICAgICAgIHRoaXMuYWN0aXZhdGVFeGNsdXNpdmUoKTtcbiAgICAgICAgdGhpcy5zb3J0UHJvamVjdFRpbGVzKCk7XG4gICAgICAgIHRoaXMuX3NhdmVTdGF0ZVRvTG9jYWxTdG9yYWdlKCk7XG4gICAgfVxuICAgIC8vIGFkZHMgY2xhc3MgYGFjdGl2ZWAgdG8gYWN0aXZlIGJ1dHRvbiBhbmQgcmVtb3ZlcyBpdCBmcm9tIGFsbCBvdGhlcnMuXG4gICAgYWN0aXZhdGVFeGNsdXNpdmUoKTogdm9pZCB7XG4gICAgICAgIGNvbnN0IGJ0bnM6IFN5c3RvcmlTb3J0QnV0dG9uW10gPSBBcnJheS5mcm9tKFxuICAgICAgICAgICAgZG9jdW1lbnQucXVlcnlTZWxlY3RvckFsbChcInN5cy1zb3J0LWJ1dHRvblwiKSxcbiAgICAgICAgKTtcbiAgICAgICAgZm9yIChjb25zdCBidG4gb2YgYnRucykge1xuICAgICAgICAgICAgYnRuLmFjdGl2ZSA9IGZhbHNlO1xuICAgICAgICB9XG4gICAgICAgIHRoaXMuYWN0aXZlID0gdHJ1ZTtcbiAgICB9XG5cbiAgICBzb3J0UHJvamVjdFRpbGVzKCk6IHZvaWQge1xuICAgICAgICBjb25zdCBwcm9qZWN0VGlsZXMgPSBBcnJheS5mcm9tKFxuICAgICAgICAgICAgZG9jdW1lbnQucXVlcnlTZWxlY3RvckFsbDxTeXN0b3JpUHJvamVjdFRpbGU+KFwiLnRpbGVcIiksXG4gICAgICAgICk7XG5cbiAgICAgICAgcHJvamVjdFRpbGVzLnNvcnQoKGEsIGIpID0+IHtcbiAgICAgICAgICAgIHN3aXRjaCAodGhpcy50eXBlKSB7XG4gICAgICAgICAgICAgICAgY2FzZSBTb3J0QnV0dG9uVHlwZS5pZDpcbiAgICAgICAgICAgICAgICAgICAgaWYgKHRoaXMuYXNjKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICByZXR1cm4gYi5wayA8IGEucGsgPyAtMSA6IDE7XG4gICAgICAgICAgICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICAgICAgICAgICAgICByZXR1cm4gYS5wayA8IGIucGsgPyAtMSA6IDE7XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICBjYXNlIFNvcnRCdXR0b25UeXBlLm5hbWU6XG4gICAgICAgICAgICAgICAgICAgIC8vIFRvRG86IHN3aXRjaCB4LmRhdGFzZXQubmFtZSEgYmFjayB0byB4Lm5hbWUgaWYgaXQgd29ya3Mgd2l0aCBfbG9hZFN0YXRlRnJvbUxvY2FsU3RvcmFnZVxuICAgICAgICAgICAgICAgICAgICBpZiAodGhpcy5hc2MpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIHJldHVybiBhLmRhdGFzZXQubmFtZSEubG9jYWxlQ29tcGFyZShiLmRhdGFzZXQubmFtZSEpO1xuICAgICAgICAgICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgICAgICAgICAgcmV0dXJuIGIuZGF0YXNldC5uYW1lIS5sb2NhbGVDb21wYXJlKGEuZGF0YXNldC5uYW1lISk7XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICBjYXNlIFNvcnRCdXR0b25UeXBlLnBoYXNlOlxuICAgICAgICAgICAgICAgICAgICBpZiAodGhpcy5hc2MpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIHJldHVybiBQaGFzZU9yZGVyW2IucGhhc2VdIDw9IFBoYXNlT3JkZXJbYS5waGFzZV1cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICA/IC0xXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgOiAxO1xuICAgICAgICAgICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgICAgICAgICAgcmV0dXJuIFBoYXNlT3JkZXJbYS5waGFzZV0gPD0gUGhhc2VPcmRlcltiLnBoYXNlXVxuICAgICAgICAgICAgICAgICAgICAgICAgICAgID8gLTFcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICA6IDE7XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICBkZWZhdWx0OlxuICAgICAgICAgICAgICAgICAgICB0aHJvdyBuZXcgRXJyb3IoXG4gICAgICAgICAgICAgICAgICAgICAgICBgQ2FuJ3QgZmluZCBhIFNvcnRCdXR0b25UeXBlIHR5cGUgZm9yICR7dGhpcy50eXBlfS5gLFxuICAgICAgICAgICAgICAgICAgICApO1xuICAgICAgICAgICAgfVxuICAgICAgICB9KTtcblxuICAgICAgICBpZiAodGlsZUNvbnRhaW5lcikge1xuICAgICAgICAgICAgdGlsZUNvbnRhaW5lci5pbm5lckhUTUwgPSBcIlwiO1xuICAgICAgICAgICAgZm9yIChjb25zdCB0aWxlIG9mIHByb2plY3RUaWxlcykge1xuICAgICAgICAgICAgICAgIHRpbGVDb250YWluZXIuYXBwZW5kQ2hpbGQodGlsZSk7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cblxuICAgICAgICB0aGlzLl9zYXZlU3RhdGVUb0xvY2FsU3RvcmFnZSgpO1xuICAgIH1cblxuICAgIF9zYXZlU3RhdGVUb0xvY2FsU3RvcmFnZSgpOiB2b2lkIHtcbiAgICAgICAgbG9jYWxTdG9yYWdlLnNldEl0ZW0oXG4gICAgICAgICAgICBcInN0YXRlLVN5c3RvcmlTb3J0QnV0dG9uXCIsXG4gICAgICAgICAgICBKU09OLnN0cmluZ2lmeSh7XG4gICAgICAgICAgICAgICAgdHlwZTogdGhpcy50eXBlLFxuICAgICAgICAgICAgICAgIGFzYzogdGhpcy5hc2MsXG4gICAgICAgICAgICB9KSxcbiAgICAgICAgKTtcbiAgICB9XG4gICAgX2xvYWRTdGF0ZUZyb21Mb2NhbFN0b3JhZ2UoKTogdm9pZCB7XG4gICAgICAgIGlmICh0aGlzLmFjdGl2ZSB8fCAhdGhpcy5hY3RpdmUpIHtcbiAgICAgICAgICAgIGNvbnN0IHNvcnRKc29uID0gbG9jYWxTdG9yYWdlLmdldEl0ZW0oXCJzdGF0ZS1TeXN0b3JpU29ydEJ1dHRvblwiKTtcbiAgICAgICAgICAgIGlmIChzb3J0SnNvbikge1xuICAgICAgICAgICAgICAgIGNvbnN0IHN0YXRlOiBTb3J0QnV0dG9uU3RhdGUgPSBKU09OLnBhcnNlKHNvcnRKc29uKTtcbiAgICAgICAgICAgICAgICBpZiAodGhpcy50eXBlID09PSBzdGF0ZS50eXBlKSB7XG4gICAgICAgICAgICAgICAgICAgIHRoaXMuYXNjID0gc3RhdGUuYXNjO1xuICAgICAgICAgICAgICAgICAgICB0aGlzLmFjdGl2ZSA9IHRydWU7XG4gICAgICAgICAgICAgICAgICAgIHRoaXMuc29ydFByb2plY3RUaWxlcygpO1xuICAgICAgICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICAgICAgICAgIGRlbGV0ZSB0aGlzLmRhdGFzZXQuYWN0aXZlO1xuICAgICAgICAgICAgICAgICAgICB0aGlzLmFjdGl2ZSA9IGZhbHNlO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgIH1cbiAgICBjb25uZWN0ZWRDYWxsYmFjaygpOiB2b2lkIHtcbiAgICAgICAgdGhpcy5fbG9hZFN0YXRlRnJvbUxvY2FsU3RvcmFnZSgpO1xuICAgIH1cbn1cblxuY2xhc3MgU3lzdG9yaVBoYXNlQnV0dG9uIGV4dGVuZHMgSFRNTEVsZW1lbnQge1xuICAgIGNvbnN0cnVjdG9yKCkge1xuICAgICAgICBzdXBlcigpO1xuICAgICAgICB0aGlzLmFkZEV2ZW50TGlzdGVuZXIoXCJjbGlja1wiLCAoKSA9PiB0aGlzLmNsaWNrSGFuZGxlcigpKTtcbiAgICB9XG5cbiAgICBnZXQgcGhhc2UoKTogc3RyaW5nIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuZGF0YXNldC5waGFzZSE7XG4gICAgfVxuICAgIHNldCBwaGFzZShwaGFzZTogc3RyaW5nKSB7XG4gICAgICAgIHRoaXMuZGF0YXNldC5waGFzZSA9IHBoYXNlO1xuICAgIH1cblxuICAgIC8vIGhpZGVQaGFzZSA9PT0gaGlkZGVuXG4gICAgZ2V0IGhpZGVQaGFzZSgpOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuY2xhc3NMaXN0LmNvbnRhaW5zKFwiaGlkZS1waGFzZVwiKTtcbiAgICB9XG4gICAgc2V0IGhpZGVQaGFzZShoaWRlOiBib29sZWFuKSB7XG4gICAgICAgIGhpZGVcbiAgICAgICAgICAgID8gdGhpcy5jbGFzc0xpc3QuYWRkKFwiaGlkZS1waGFzZVwiKVxuICAgICAgICAgICAgOiB0aGlzLmNsYXNzTGlzdC5yZW1vdmUoXCJoaWRlLXBoYXNlXCIpO1xuICAgIH1cbiAgICB0b2dnbGVQcm9qZWN0VGlsZXMoc3RhdHVzOiBib29sZWFuKTogdm9pZCB7XG4gICAgICAgIGNvbnN0IHByb2plY3RUaWxlczogU3lzdG9yaVByb2plY3RUaWxlW10gPSBBcnJheS5mcm9tKFxuICAgICAgICAgICAgZG9jdW1lbnQucXVlcnlTZWxlY3RvckFsbChcbiAgICAgICAgICAgICAgICBgc3lzLXByb2plY3QtdGlsZVtkYXRhLXBoYXNlPSR7dGhpcy5waGFzZX1dYCxcbiAgICAgICAgICAgICksXG4gICAgICAgICk7XG4gICAgICAgIGZvciAoY29uc3QgdGlsZSBvZiBwcm9qZWN0VGlsZXMpIHtcbiAgICAgICAgICAgIHRpbGUuaGlkZShzdGF0dXMpO1xuICAgICAgICB9XG4gICAgfVxuICAgIGNsaWNrSGFuZGxlcigpOiB2b2lkIHtcbiAgICAgICAgdGhpcy5oaWRlUGhhc2UgPSAhdGhpcy5oaWRlUGhhc2U7XG4gICAgICAgIHRoaXMuZmlsdGVyUHJvamVjdFRpbGVzKCk7XG4gICAgICAgIHRoaXMuX3NhdmVTdGF0ZVRvTG9jYWxTdG9yYWdlKCk7XG4gICAgfVxuICAgIGZpbHRlclByb2plY3RUaWxlcygpOiB2b2lkIHtcbiAgICAgICAgdGhpcy5oaWRlUGhhc2VcbiAgICAgICAgICAgID8gdGhpcy50b2dnbGVQcm9qZWN0VGlsZXModHJ1ZSlcbiAgICAgICAgICAgIDogdGhpcy50b2dnbGVQcm9qZWN0VGlsZXMoZmFsc2UpO1xuICAgIH1cbiAgICBfc2F2ZVN0YXRlVG9Mb2NhbFN0b3JhZ2UoKTogdm9pZCB7XG4gICAgICAgIGxvY2FsU3RvcmFnZS5zZXRJdGVtKFxuICAgICAgICAgICAgYHN0YXRlLVN5c3RvcmlQaGFzZUJ1dHRvbi0ke3RoaXMucGhhc2V9YCxcbiAgICAgICAgICAgIEpTT04uc3RyaW5naWZ5KHtcbiAgICAgICAgICAgICAgICBoaWRlUGhhc2U6IHRoaXMuaGlkZVBoYXNlLFxuICAgICAgICAgICAgfSksXG4gICAgICAgICk7XG4gICAgfVxuICAgIF9sb2FkU3RhdGVGcm9tTG9jYWxTdG9yYWdlKCk6IHZvaWQge1xuICAgICAgICBjb25zdCBzdGF0ZUpzb24gPSBsb2NhbFN0b3JhZ2UuZ2V0SXRlbShcbiAgICAgICAgICAgIGBzdGF0ZS1TeXN0b3JpUGhhc2VCdXR0b24tJHt0aGlzLnBoYXNlfWAsXG4gICAgICAgICk7XG4gICAgICAgIGlmIChzdGF0ZUpzb24pIHtcbiAgICAgICAgICAgIGNvbnN0IHN0YXRlID0gSlNPTi5wYXJzZShzdGF0ZUpzb24pO1xuICAgICAgICAgICAgdGhpcy5oaWRlUGhhc2UgPSBzdGF0ZS5oaWRlUGhhc2U7XG4gICAgICAgICAgICB0aGlzLmZpbHRlclByb2plY3RUaWxlcygpO1xuICAgICAgICB9XG4gICAgfVxuICAgIGNvbm5lY3RlZENhbGxiYWNrKCk6IHZvaWQge1xuICAgICAgICB0aGlzLl9sb2FkU3RhdGVGcm9tTG9jYWxTdG9yYWdlKCk7XG4gICAgfVxufVxuXG5jbGFzcyBTeXN0b3JpU2VhcmNoRWxlbWVudCBleHRlbmRzIEhUTUxFbGVtZW50IHtcbiAgICAvLyBUaGlzIGN1c3RvbSBlbGVtZW50IGlzIGZvciBjb21wb3NpbmcgdGhlIHR3byBjaGlsZE5vZGVzLlxuICAgIGNvbnN0cnVjdG9yKCkge1xuICAgICAgICBzdXBlcigpO1xuICAgIH1cbn1cblxuY2xhc3MgU3lzdG9yaVNlYXJjaElucHV0IGV4dGVuZHMgSFRNTElucHV0RWxlbWVudCB7XG4gICAgdGltZW91dDogUmV0dXJuVHlwZTx0eXBlb2Ygc2V0VGltZW91dD4gfCB1bmRlZmluZWQ7XG5cbiAgICBjb25zdHJ1Y3RvcigpIHtcbiAgICAgICAgc3VwZXIoKTtcbiAgICAgICAgdGhpcy5hZGRFdmVudExpc3RlbmVyKFwia2V5dXBcIiwgKCkgPT4gdGhpcy5jbGlja0hhbmRsZXIoKSk7XG4gICAgfVxuXG4gICAgZmlsdGVyUHJvamVjdFRpbGVzKHNlYXJjaFJlc3VsdFBrczogbnVtYmVyW10pOiB2b2lkIHtcbiAgICAgICAgY29uc3QgcHJvamVjdFBrcyA9IHRoaXMuZ2V0QWxsTG9jYWxQcm9qZWN0UGtzKCk7XG4gICAgICAgIC8vIGFsbCBwcm9qZWN0cyBleGNlcHQgdGhlIGZvdW5kIHByb2plY3RzXG4gICAgICAgIGNvbnN0IGRpZmZlcmVuY2UgPSBwcm9qZWN0UGtzLmZpbHRlcihcbiAgICAgICAgICAgIHBrID0+ICFzZWFyY2hSZXN1bHRQa3MuaW5jbHVkZXMocGspLFxuICAgICAgICApO1xuICAgICAgICBmb3IgKGNvbnN0IHBrIG9mIGRpZmZlcmVuY2UpIHtcbiAgICAgICAgICAgIGNvbnN0IHRpbGUgPSBkb2N1bWVudC5xdWVyeVNlbGVjdG9yPFN5c3RvcmlQcm9qZWN0VGlsZT4oXG4gICAgICAgICAgICAgICAgYHN5cy1wcm9qZWN0LXRpbGVbZGF0YS1waz1cIiR7cGt9XCJdYCxcbiAgICAgICAgICAgICk7XG4gICAgICAgICAgICBpZiAodGlsZSkgdGlsZS5oaWRlKHRydWUpO1xuICAgICAgICB9XG4gICAgfVxuXG4gICAgc2hvd0FsbFByb2plY3RzKCk6IHZvaWQge1xuICAgICAgICBjb25zdCBwaGFzZUJ0bnMgPSBuZXcgTWFwKCk7XG4gICAgICAgIEFycmF5LmZyb20oXG4gICAgICAgICAgICBkb2N1bWVudC5xdWVyeVNlbGVjdG9yQWxsPFN5c3RvcmlQaGFzZUJ1dHRvbj4oXCJzeXMtcGhhc2UtYnV0dG9uXCIpLFxuICAgICAgICApLm1hcCh0aWxlID0+IHBoYXNlQnRucy5zZXQodGlsZS5waGFzZSwgdGlsZS5oaWRlUGhhc2UpKTtcbiAgICAgICAgY29uc3QgcHJvamVjdFBrcyA9IHRoaXMuZ2V0QWxsTG9jYWxQcm9qZWN0UGtzKCk7XG4gICAgICAgIGZvciAoY29uc3QgcGsgb2YgcHJvamVjdFBrcykge1xuICAgICAgICAgICAgY29uc3QgdGlsZSA9IGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3I8U3lzdG9yaVByb2plY3RUaWxlPihcbiAgICAgICAgICAgICAgICBgc3lzLXByb2plY3QtdGlsZVtkYXRhLXBrPVwiJHtwa31cIl1gLFxuICAgICAgICAgICAgKTtcbiAgICAgICAgICAgIGlmICh0aWxlICYmICFwaGFzZUJ0bnMuZ2V0KHRpbGUucGhhc2UpKSB0aWxlLmhpZGUoZmFsc2UpO1xuICAgICAgICB9XG4gICAgICAgIGNvbnN0IGNhbmNlbEJ1dHRvbiA9IGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3I8U3lzdG9yaVNlYXJjaENhbmNlbEJ1dHRvbj4oXG4gICAgICAgICAgICBcInN5cy1zZWFyY2gtY2FuY2VsLWJ1dHRvblwiLFxuICAgICAgICApITtcbiAgICAgICAgY2FuY2VsQnV0dG9uLnZpc2libGUgPSBmYWxzZTtcbiAgICB9XG5cbiAgICBnZXRBbGxMb2NhbFByb2plY3RQa3MoKTogbnVtYmVyW10ge1xuICAgICAgICByZXR1cm4gQXJyYXkuZnJvbShcbiAgICAgICAgICAgIGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGw8U3lzdG9yaVByb2plY3RUaWxlPihgc3lzLXByb2plY3QtdGlsZWApLFxuICAgICAgICApLm1hcCh0aWxlID0+IHtcbiAgICAgICAgICAgIHJldHVybiB0aWxlLnBrO1xuICAgICAgICB9KTtcbiAgICB9XG5cbiAgICBhcGlTZWFyY2hQcm9qZWN0cygpOiB2b2lkIHtcbiAgICAgICAgbG9jYWxTdG9yYWdlLnNldEl0ZW0oXCJzeXMtcHJvamVjdC1zZWFyY2gtaW5wdXRcIiwgdGhpcy52YWx1ZSk7XG4gICAgICAgIGZldGNoKFwiL2FwaS9wcm9qZWN0L3NlYXJjaC9cIiwge1xuICAgICAgICAgICAgbWV0aG9kOiBcInB1dFwiLFxuICAgICAgICAgICAgY3JlZGVudGlhbHM6IFwic2FtZS1vcmlnaW5cIixcbiAgICAgICAgICAgIGhlYWRlcnM6IGhlYWRlcnMsXG4gICAgICAgICAgICBib2R5OiBKU09OLnN0cmluZ2lmeSh7IHF1ZXJ5OiB0aGlzLnZhbHVlIH0pLFxuICAgICAgICB9KVxuICAgICAgICAgICAgLnRoZW4ocmVzcG9uc2UgPT4gcmVzcG9uc2UuanNvbigpKVxuICAgICAgICAgICAgLnRoZW4oYm9keSA9PiB7XG4gICAgICAgICAgICAgICAgdGhpcy5maWx0ZXJQcm9qZWN0VGlsZXMoYm9keS5wcm9qZWN0cyk7XG4gICAgICAgICAgICB9KTtcbiAgICB9XG5cbiAgICBwcm9jZXNzUXVlcnkoKTogdm9pZCB7XG4gICAgICAgIGNvbnN0IGNhbmNlbEJ1dHRvbiA9IGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3I8U3lzdG9yaVNlYXJjaENhbmNlbEJ1dHRvbj4oXG4gICAgICAgICAgICBcInN5cy1zZWFyY2gtY2FuY2VsLWJ1dHRvblwiLFxuICAgICAgICApITtcbiAgICAgICAgY2FuY2VsQnV0dG9uLnZpc2libGUgPSB0cnVlO1xuICAgICAgICB0aGlzLmFwaVNlYXJjaFByb2plY3RzKCk7XG4gICAgfVxuXG4gICAgZGVsYXllZENsaWNrSGFuZGxlcigpOiB2b2lkIHtcbiAgICAgICAgdGhpcy52YWx1ZSA9PSBcIlwiID8gdGhpcy5zaG93QWxsUHJvamVjdHMoKSA6IHRoaXMucHJvY2Vzc1F1ZXJ5KCk7XG4gICAgfVxuXG4gICAgY2xpY2tIYW5kbGVyKCk6IHZvaWQge1xuICAgICAgICBpZiAodGhpcy50aW1lb3V0KSBjbGVhclRpbWVvdXQodGhpcy50aW1lb3V0KTtcbiAgICAgICAgdGhpcy50aW1lb3V0ID0gc2V0VGltZW91dCgoKSA9PiB7XG4gICAgICAgICAgICB0aGlzLnZhbHVlID09IFwiXCIgPyB0aGlzLnNob3dBbGxQcm9qZWN0cygpIDogdGhpcy5wcm9jZXNzUXVlcnkoKTtcbiAgICAgICAgfSwgMzAwKTtcbiAgICB9XG59XG5cbmNsYXNzIFN5c3RvcmlTZWFyY2hDYW5jZWxCdXR0b24gZXh0ZW5kcyBIVE1MRWxlbWVudCB7XG4gICAgY29uc3RydWN0b3IoKSB7XG4gICAgICAgIHN1cGVyKCk7XG4gICAgICAgIHRoaXMuYWRkRXZlbnRMaXN0ZW5lcihcImNsaWNrXCIsICgpID0+IHRoaXMuY2xpY2tIYW5kbGVyKCkpO1xuICAgIH1cbiAgICBnZXQgdmlzaWJsZSgpOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuY2xhc3NMaXN0LmNvbnRhaW5zKFwidmlzaWJsZVwiKTtcbiAgICB9XG4gICAgc2V0IHZpc2libGUoc3RhdHVzOiBib29sZWFuKSB7XG4gICAgICAgIHRoaXMuY2xhc3NMaXN0LnRvZ2dsZShcInZpc2libGVcIiwgc3RhdHVzKTtcbiAgICB9XG4gICAgY2xpY2tIYW5kbGVyKCk6IHZvaWQge1xuICAgICAgICBpZiAodGhpcy5wYXJlbnRFbGVtZW50KSB7XG4gICAgICAgICAgICBjb25zdCBpbnB1dCA9IHRoaXMucGFyZW50RWxlbWVudC5xdWVyeVNlbGVjdG9yPFN5c3RvcmlTZWFyY2hJbnB1dD4oXG4gICAgICAgICAgICAgICAgJ2lucHV0W2lzPVwic3lzLXNlYXJjaC1pbnB1dFwiXScsXG4gICAgICAgICAgICApO1xuICAgICAgICAgICAgaWYgKGlucHV0KSB7XG4gICAgICAgICAgICAgICAgaW5wdXQudmFsdWUgPSBcIlwiO1xuICAgICAgICAgICAgICAgIGlucHV0LnNob3dBbGxQcm9qZWN0cygpO1xuICAgICAgICAgICAgICAgIHRoaXMudmlzaWJsZSA9IGZhbHNlO1xuICAgICAgICAgICAgfVxuICAgICAgICB9XG4gICAgfVxufVxuXG5jdXN0b21FbGVtZW50cy5kZWZpbmUoXCJzeXMtcHJvamVjdC10aWxlXCIsIFN5c3RvcmlQcm9qZWN0VGlsZSk7XG5jdXN0b21FbGVtZW50cy5kZWZpbmUoXCJzeXMtc2VhcmNoLWlucHV0XCIsIFN5c3RvcmlTZWFyY2hJbnB1dCwge1xuICAgIGV4dGVuZHM6IFwiaW5wdXRcIixcbn0pO1xuY3VzdG9tRWxlbWVudHMuZGVmaW5lKFwic3lzLXNlYXJjaC1lbGVtZW50XCIsIFN5c3RvcmlTZWFyY2hFbGVtZW50KTtcbmN1c3RvbUVsZW1lbnRzLmRlZmluZShcInN5cy1zZWFyY2gtY2FuY2VsLWJ1dHRvblwiLCBTeXN0b3JpU2VhcmNoQ2FuY2VsQnV0dG9uKTtcbmN1c3RvbUVsZW1lbnRzLmRlZmluZShcInN5cy1waGFzZS1idXR0b25cIiwgU3lzdG9yaVBoYXNlQnV0dG9uKTtcbmN1c3RvbUVsZW1lbnRzLmRlZmluZShcInN5cy1zb3J0LWJ1dHRvblwiLCBTeXN0b3JpU29ydEJ1dHRvbik7XG5cbi8vIGxvYWRMb2NhbFN0b3JhZ2UoKTtcbmlmIChmaWx0ZXJCYXIpIHtcbiAgICBmaWx0ZXJCYXIuY2xhc3NMaXN0LnJlbW92ZShcImhpZGRlblwiKTtcbn1cbmlmICh0aWxlQ29udGFpbmVyKSB7XG4gICAgdGlsZUNvbnRhaW5lci5jbGFzc0xpc3QucmVtb3ZlKFwiaGlkZGVuXCIpO1xufVxuIl0sInNvdXJjZVJvb3QiOiIifQ==