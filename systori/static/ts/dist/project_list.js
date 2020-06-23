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
        this.showWarningMessage();
        this._saveStateToLocalStorage();
    }
    filterProjectTiles() {
        this.hidePhase
            ? this.toggleProjectTiles(true)
            : this.toggleProjectTiles(false);
    }
    showWarningMessage() {
        let hiddenProjectTiles = document.querySelectorAll(".tile.hidden");
        let sysWarningMessage = document.querySelector("sys-warning-message");
        if (sysWarningMessage)
            sysWarningMessage.warnFilteredProjects(hiddenProjectTiles.length || 0);
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
            this.showWarningMessage();
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
        const sysWarningMessage = document.querySelector("sys-warning-message");
        if (sysWarningMessage)
            sysWarningMessage.warnFilteredProjects(difference.length);
    }
    showAllVisibleProjects() {
        const phaseBtns = new Map();
        Array.from(document.querySelectorAll("sys-phase-button")).map(tile => phaseBtns.set(tile.phase, tile.hidePhase));
        const projectPks = this.getAllLocalProjectPks();
        var countHiddenProjects = projectPks.length;
        for (const pk of projectPks) {
            const tile = document.querySelector(`sys-project-tile[data-pk="${pk}"]`);
            if (tile && !phaseBtns.get(tile.phase)) {
                tile.hide(false);
                countHiddenProjects--;
            }
        }
        const cancelButton = document.querySelector("sys-search-cancel-button");
        cancelButton.visible = false;
        const sysWarningMessage = document.querySelector("sys-warning-message");
        if (sysWarningMessage)
            sysWarningMessage.warnFilteredProjects(countHiddenProjects);
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
        this.value == "" ? this.showAllVisibleProjects() : this.processQuery();
    }
    clickHandler() {
        if (this.timeout)
            clearTimeout(this.timeout);
        this.timeout = setTimeout(() => {
            this.value == "" ? this.showAllVisibleProjects() : this.processQuery();
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
                input.showAllVisibleProjects();
                this.visible = false;
            }
        }
    }
}
class SystoriWarningMessage extends HTMLElement {
    constructor() {
        super();
    }
    warnFilteredProjects(count) {
        let regex = /\$phaseFilteredProjects/gi;
        if (count > 0) {
            this.innerText = document.querySelector("#sys-phaseFilteredProjects-translated").innerText.replace(regex, count.toString());
            this.classList.remove("hidden");
        }
        else {
            this.classList.add("hidden");
        }
    }
    get hideWarningMessage() {
        return this.classList.contains('hidden');
    }
    set hideWarningMessage(hide) {
        hide
            ? this.classList.add('hidden')
            : this.classList.remove('hidden');
    }
}
customElements.define("sys-warning-message", SystoriWarningMessage);
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
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8vd2VicGFjay9ib290c3RyYXAiLCJ3ZWJwYWNrOi8vLy4vc3JjL3Byb2plY3RfbGlzdC50cyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiO1FBQUE7UUFDQTs7UUFFQTtRQUNBOztRQUVBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBOztRQUVBO1FBQ0E7O1FBRUE7UUFDQTs7UUFFQTtRQUNBO1FBQ0E7OztRQUdBO1FBQ0E7O1FBRUE7UUFDQTs7UUFFQTtRQUNBO1FBQ0E7UUFDQSwwQ0FBMEMsZ0NBQWdDO1FBQzFFO1FBQ0E7O1FBRUE7UUFDQTtRQUNBO1FBQ0Esd0RBQXdELGtCQUFrQjtRQUMxRTtRQUNBLGlEQUFpRCxjQUFjO1FBQy9EOztRQUVBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQSx5Q0FBeUMsaUNBQWlDO1FBQzFFLGdIQUFnSCxtQkFBbUIsRUFBRTtRQUNySTtRQUNBOztRQUVBO1FBQ0E7UUFDQTtRQUNBLDJCQUEyQiwwQkFBMEIsRUFBRTtRQUN2RCxpQ0FBaUMsZUFBZTtRQUNoRDtRQUNBO1FBQ0E7O1FBRUE7UUFDQSxzREFBc0QsK0RBQStEOztRQUVySDtRQUNBOzs7UUFHQTtRQUNBOzs7Ozs7Ozs7Ozs7OztBQ2pGQSxTQUFTLFNBQVMsQ0FBQyxLQUFhO0lBQzVCLE1BQU0sT0FBTyxHQUFHLFFBQVEsQ0FBQyxNQUFNLENBQUMsS0FBSyxDQUFDLEdBQUcsQ0FBQyxDQUFDO0lBQzNDLEtBQUssTUFBTSxNQUFNLElBQUksT0FBTyxFQUFFO1FBQzFCLE1BQU0sQ0FBQyxJQUFJLEVBQUUsS0FBSyxDQUFDLEdBQUcsTUFBTSxDQUFDLEtBQUssQ0FBQyxHQUFHLENBQUMsQ0FBQztRQUN4QyxJQUFJLElBQUksS0FBSyxLQUFLLEVBQUU7WUFDaEIsT0FBTyxLQUFLLENBQUM7U0FDaEI7S0FDSjtJQUNELE9BQU8sRUFBRSxDQUFDO0FBQ2QsQ0FB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U0FBUyxDQUFDLE1BQU0sQ0FBQyxRQUFRLENBQUMsQ0FBQztDQUM1QyIsImZpbGUiOiJwcm9qZWN0X2xpc3QuanMiLCJzb3VyY2VzQ29udGVudCI6WyIgXHQvLyBUaGUgbW9kdWxlIGNhY2hlXG4gXHR2YXIgaW5zdGFsbGVkTW9kdWxlcyA9IHt9O1xuXG4gXHQvLyBUaGUgcmVxdWlyZSBmdW5jdGlvblxuIFx0ZnVuY3Rpb24gX193ZWJwYWNrX3JlcXVpcmVfXyhtb2R1bGVJZCkge1xuXG4gXHRcdC8vIENoZWNrIGlmIG1vZHVsZSBpcyBpbiBjYWNoZVxuIFx0XHRpZihpbnN0YWxsZWRNb2R1bGVzW21vZHVsZUlkXSkge1xuIFx0XHRcdHJldHVybiBpbnN0YWxsZWRNb2R1bGVzW21vZHVsZUlkXS5leHBvcnRzO1xuIFx0XHR9XG4gXHRcdC8vIENyZWF0ZSBhIG5ldyBtb2R1bGUgKGFuZCBwdXQgaXQgaW50byB0aGUgY2FjaGUpXG4gXHRcdHZhciBtb2R1bGUgPSBpbnN0YWxsZWRNb2R1bGVzW21vZHVsZUlkXSA9IHtcbiBcdFx0XHRpOiBtb2R1bGVJZCxcbiBcdFx0XHRsOiBmYWxzZSxcbiBcdFx0XHRleHBvcnRzOiB7fVxuIFx0XHR9O1xuXG4gXHRcdC8vIEV4ZWN1dGUgdGhlIG1vZHVsZSBmdW5jdGlvblxuIFx0XHRtb2R1bGVzW21vZHVsZUlkXS5jYWxsKG1vZHVsZS5leHBvcnRzLCBtb2R1bGUsIG1vZHVsZS5leHBvcnRzLCBfX3dlYnBhY2tfcmVxdWlyZV9fKTtcblxuIFx0XHQvLyBGbGFnIHRoZSBtb2R1bGUgYXMgbG9hZGVkXG4gXHRcdG1vZHVsZS5sID0gdHJ1ZTtcblxuIFx0XHQvLyBSZXR1cm4gdGhlIGV4cG9ydHMgb2YgdGhlIG1vZHVsZVxuIFx0XHRyZXR1cm4gbW9kdWxlLmV4cG9ydHM7XG4gXHR9XG5cblxuIFx0Ly8gZXhwb3NlIHRoZSBtb2R1bGVzIG9iamVjdCAoX193ZWJwYWNrX21vZHVsZXNfXylcbiBcdF9fd2VicGFja19yZXF1aXJlX18ubSA9IG1vZHVsZXM7XG5cbiBcdC8vIGV4cG9zZSB0aGUgbW9kdWxlIGNhY2hlXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLmMgPSBpbnN0YWxsZWRNb2R1bGVzO1xuXG4gXHQvLyBkZWZpbmUgZ2V0dGVyIGZ1bmN0aW9uIGZvciBoYXJtb255IGV4cG9ydHNcbiBcdF9fd2VicGFja19yZXF1aXJlX18uZCA9IGZ1bmN0aW9uKGV4cG9ydHMsIG5hbWUsIGdldHRlcikge1xuIFx0XHRpZighX193ZWJwYWNrX3JlcXVpcmVfXy5vKGV4cG9ydHMsIG5hbWUpKSB7XG4gXHRcdFx0T2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIG5hbWUsIHsgZW51bWVyYWJsZTogdHJ1ZSwgZ2V0OiBnZXR0ZXIgfSk7XG4gXHRcdH1cbiBcdH07XG5cbiBcdC8vIGRlZmluZSBfX2VzTW9kdWxlIG9uIGV4cG9ydHNcbiBcdF9fd2VicGFja19yZXF1aXJlX18uciA9IGZ1bmN0aW9uKGV4cG9ydHMpIHtcbiBcdFx0aWYodHlwZW9mIFN5bWJvbCAhPT0gJ3VuZGVmaW5lZCcgJiYgU3ltYm9sLnRvU3RyaW5nVGFnKSB7XG4gXHRcdFx0T2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIFN5bWJvbC50b1N0cmluZ1RhZywgeyB2YWx1ZTogJ01vZHVsZScgfSk7XG4gXHRcdH1cbiBcdFx0T2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsICdfX2VzTW9kdWxlJywgeyB2YWx1ZTogdHJ1ZSB9KTtcbiBcdH07XG5cbiBcdC8vIGNyZWF0ZSBhIGZha2UgbmFtZXNwYWNlIG9iamVjdFxuIFx0Ly8gbW9kZSAmIDE6IHZhbHVlIGlzIGEgbW9kdWxlIGlkLCByZXF1aXJlIGl0XG4gXHQvLyBtb2RlICYgMjogbWVyZ2UgYWxsIHByb3BlcnRpZXMgb2YgdmFsdWUgaW50byB0aGUgbnNcbiBcdC8vIG1vZGUgJiA0OiByZXR1cm4gdmFsdWUgd2hlbiBhbHJlYWR5IG5zIG9iamVjdFxuIFx0Ly8gbW9kZSAmIDh8MTogYmVoYXZlIGxpa2UgcmVxdWlyZVxuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy50ID0gZnVuY3Rpb24odmFsdWUsIG1vZGUpIHtcbiBcdFx0aWYobW9kZSAmIDEpIHZhbHVlID0gX193ZWJwYWNrX3JlcXVpcmVfXyh2YWx1ZSk7XG4gXHRcdGlmKG1vZGUgJiA4KSByZXR1cm4gdmFsdWU7XG4gXHRcdGlmKChtb2RlICYgNCkgJiYgdHlwZW9mIHZhbHVlID09PSAnb2JqZWN0JyAmJiB2YWx1ZSAmJiB2YWx1ZS5fX2VzTW9kdWxlKSByZXR1cm4gdmFsdWU7XG4gXHRcdHZhciBucyA9IE9iamVjdC5jcmVhdGUobnVsbCk7XG4gXHRcdF9fd2VicGFja19yZXF1aXJlX18ucihucyk7XG4gXHRcdE9iamVjdC5kZWZpbmVQcm9wZXJ0eShucywgJ2RlZmF1bHQnLCB7IGVudW1lcmFibGU6IHRydWUsIHZhbHVlOiB2YWx1ZSB9KTtcbiBcdFx0aWYobW9kZSAmIDIgJiYgdHlwZW9mIHZhbHVlICE9ICdzdHJpbmcnKSBmb3IodmFyIGtleSBpbiB2YWx1ZSkgX193ZWJwYWNrX3JlcXVpcmVfXy5kKG5zLCBrZXksIGZ1bmN0aW9uKGtleSkgeyByZXR1cm4gdmFsdWVba2V5XTsgfS5iaW5kKG51bGwsIGtleSkpO1xuIFx0XHRyZXR1cm4gbnM7XG4gXHR9O1xuXG4gXHQvLyBnZXREZWZhdWx0RXhwb3J0IGZ1bmN0aW9uIGZvciBjb21wYXRpYmlsaXR5IHdpdGggbm9uLWhhcm1vbnkgbW9kdWxlc1xuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy5uID0gZnVuY3Rpb24obW9kdWxlKSB7XG4gXHRcdHZhciBnZXR0ZXIgPSBtb2R1bGUgJiYgbW9kdWxlLl9fZXNNb2R1bGUgP1xuIFx0XHRcdGZ1bmN0aW9uIGdldERlZmF1bHQoKSB7IHJldHVybiBtb2R1bGVbJ2RlZmF1bHQnXTsgfSA6XG4gXHRcdFx0ZnVuY3Rpb24gZ2V0TW9kdWxlRXhwb3J0cygpIHsgcmV0dXJuIG1vZHVsZTsgfTtcbiBcdFx0X193ZWJwYWNrX3JlcXVpcmVfXy5kKGdldHRlciwgJ2EnLCBnZXR0ZXIpO1xuIFx0XHRyZXR1cm4gZ2V0dGVyO1xuIFx0fTtcblxuIFx0Ly8gT2JqZWN0LnByb3RvdHlwZS5oYXNPd25Qcm9wZXJ0eS5jYWxsXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLm8gPSBmdW5jdGlvbihvYmplY3QsIHByb3BlcnR5KSB7IHJldHVybiBPYmplY3QucHJvdG90eXBlLmhhc093blByb3BlcnR5LmNhbGwob2JqZWN0LCBwcm9wZXJ0eSk7IH07XG5cbiBcdC8vIF9fd2VicGFja19wdWJsaWNfcGF0aF9fXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLnAgPSBcIlwiO1xuXG5cbiBcdC8vIExvYWQgZW50cnkgbW9kdWxlIGFuZCByZXR1cm4gZXhwb3J0c1xuIFx0cmV0dXJuIF9fd2VicGFja19yZXF1aXJlX18oX193ZWJwYWNrX3JlcXVpcmVfXy5zID0gXCIuL3NyYy9wcm9qZWN0X2xpc3QudHNcIik7XG4iLCJcbmZ1bmN0aW9uIGdldENvb2tpZShxdWVyeTogc3RyaW5nKTogc3RyaW5nIHtcbiAgICBjb25zdCBjb29raWVzID0gZG9jdW1lbnQuY29va2llLnNwbGl0KFwiO1wiKTtcbiAgICBmb3IgKGNvbnN0IGNvb2tpZSBvZiBjb29raWVzKSB7XG4gICAgICAgIGNvbnN0IFtuYW1lLCB2YWx1ZV0gPSBjb29raWUuc3BsaXQoXCI9XCIpO1xuICAgICAgICBpZiAobmFtZSA9PT0gcXVlcnkpIHtcbiAgICAgICAgICAgIHJldHVybiB2YWx1ZTtcbiAgICAgICAgfVxuICAgIH1cbiAgICByZXR1cm4gXCJcIjtcbn1cbmNvbnN0IGZpbHRlckJhciA9IGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3IoXCIuZmlsdGVyLWJhclwiKTtcbmNvbnN0IHRpbGVDb250YWluZXIgPSBkb2N1bWVudC5xdWVyeVNlbGVjdG9yKFwiLnRpbGUtY29udGFpbmVyXCIpO1xuY29uc3QgY3NyZlRva2VuID0gZ2V0Q29va2llKFwiY3NyZnRva2VuXCIpO1xuY29uc3QgaGVhZGVycyA9IG5ldyBIZWFkZXJzKHtcbiAgICBcIkNvbnRlbnQtVHlwZVwiOiBcImFwcGxpY2F0aW9uL2pzb25cIixcbiAgICBBY2NlcHQ6IFwiYXBwbGljYXRpb24vanNvblwiLFxuICAgIFwiWC1DU1JGVG9rZW5cIjogY3NyZlRva2VuLFxufSk7XG5lbnVtIFBoYXNlT3JkZXIge1xuICAgIHByb3NwZWN0aXZlLFxuICAgIHRlbmRlcmluZyxcbiAgICBwbGFubmluZyxcbiAgICBleGVjdXRpbmcsXG4gICAgc2V0dGxlbWVudCxcbiAgICB3YXJyYW50eSxcbiAgICBmaW5pc2hlZCxcbn1cbmVudW0gU29ydEJ1dHRvblR5cGUge1xuICAgIGlkID0gXCJpZFwiLFxuICAgIG5hbWUgPSBcIm5hbWVcIixcbiAgICBwaGFzZSA9IFwicGhhc2VcIixcbn1cblxuaW50ZXJmYWNlIFNvcnRCdXR0b25TdGF0ZSB7XG4gICAgdHlwZTogU29ydEJ1dHRvblR5cGU7XG4gICAgYXNjOiBib29sZWFuO1xufVxuXG5jbGFzcyBTeXN0b3JpUHJvamVjdFRpbGUgZXh0ZW5kcyBIVE1MRWxlbWVudCB7XG4gICAgY29uc3RydWN0b3IoKSB7XG4gICAgICAgIHN1cGVyKCk7XG4gICAgfVxuICAgIGdldCBwaygpOiBudW1iZXIge1xuICAgICAgICByZXR1cm4gcGFyc2VJbnQodGhpcy5kYXRhc2V0LnBrISk7XG4gICAgfVxuICAgIGdldCBuYW1lKCk6IHN0cmluZyB7XG4gICAgICAgIHJldHVybiB0aGlzLmRhdGFzZXQubmFtZSE7XG4gICAgfVxuICAgIGdldCBwaGFzZSgpOiBQaGFzZU9yZGVyIHtcbiAgICAgICAgcmV0dXJuICh0aGlzLmRhdGFzZXQucGhhc2UgfHwgUGhhc2VPcmRlci5wcm9zcGVjdGl2ZSkgYXMgUGhhc2VPcmRlcjtcbiAgICB9XG4gICAgZ2V0IGhpZGRlbigpOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuY2xhc3NMaXN0LmNvbnRhaW5zKFwiaGlkZGVuXCIpO1xuICAgIH1cbiAgICBoaWRlKGhpZGU6IGJvb2xlYW4pOiB2b2lkIHtcbiAgICAgICAgaGlkZSA/IHRoaXMuY2xhc3NMaXN0LmFkZChcImhpZGRlblwiKSA6IHRoaXMuY2xhc3NMaXN0LnJlbW92ZShcImhpZGRlblwiKTtcbiAgICB9XG59XG5cbmNsYXNzIFN5c3RvcmlTb3J0QnV0dG9uIGV4dGVuZHMgSFRNTEVsZW1lbnQge1xuICAgIGNvbnN0cnVjdG9yKCkge1xuICAgICAgICBzdXBlcigpO1xuICAgICAgICB0aGlzLmFkZEV2ZW50TGlzdGVuZXIoXCJjbGlja1wiLCAoKSA9PiB0aGlzLmNsaWNrSGFuZGxlcigpKTtcbiAgICB9XG4gICAgZ2V0IHR5cGUoKTogU29ydEJ1dHRvblR5cGUge1xuICAgICAgICBzd2l0Y2ggKHRoaXMuZGF0YXNldC50eXBlKSB7XG4gICAgICAgICAgICBjYXNlIFwiaWRcIjpcbiAgICAgICAgICAgICAgICByZXR1cm4gU29ydEJ1dHRvblR5cGUuaWQ7XG4gICAgICAgICAgICBjYXNlIFwibmFtZVwiOlxuICAgICAgICAgICAgICAgIHJldHVybiBTb3J0QnV0dG9uVHlwZS5uYW1lO1xuICAgICAgICAgICAgY2FzZSBcInBoYXNlXCI6XG4gICAgICAgICAgICAgICAgcmV0dXJuIFNvcnRCdXR0b25UeXBlLnBoYXNlO1xuICAgICAgICAgICAgZGVmYXVsdDpcbiAgICAgICAgICAgICAgICB0aHJvdyBFcnJvcihcIkNvdWxkbid0IGNhdGNoIFNvcnRCdXR0b25UeXBlLlwiKTtcbiAgICAgICAgfVxuICAgIH1cbiAgICBzZXQgdHlwZSh0eXBlOiBTb3J0QnV0dG9uVHlwZSkge1xuICAgICAgICB0aGlzLmRhdGFzZXQudHlwZSA9IFNvcnRCdXR0b25UeXBlW3R5cGVdO1xuICAgIH1cblxuICAgIC8vIEFTQy9ERVNDIHNvcnRpbmcgb3JkZXJcbiAgICBnZXQgYXNjKCk6IGJvb2xlYW4ge1xuICAgICAgICByZXR1cm4gdGhpcy5kYXRhc2V0LmFzYyA9PSBcInRydWVcIjtcbiAgICB9XG4gICAgc2V0IGFzYyhhc2M6IGJvb2xlYW4pIHtcbiAgICAgICAgYXNjID8gKHRoaXMuZGF0YXNldC5hc2MgPSBcInRydWVcIikgOiAodGhpcy5kYXRhc2V0LmFzYyA9IFwiZmFsc2VcIik7XG4gICAgfVxuICAgIHRvZ2dsZUFzYygpOiB2b2lkIHtcbiAgICAgICAgdGhpcy5hc2MgPSAhdGhpcy5hc2M7XG4gICAgfVxuXG4gICAgZ2V0IGFjdGl2ZSgpOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuY2xhc3NMaXN0LmNvbnRhaW5zKFwiYWN0aXZlXCIpO1xuICAgIH1cbiAgICBzZXQgYWN0aXZlKHN0YXR1czogYm9vbGVhbikge1xuICAgICAgICB0aGlzLmNsYXNzTGlzdC50b2dnbGUoXCJhY3RpdmVcIiwgc3RhdHVzKTtcbiAgICB9XG5cbiAgICBjbGlja0hhbmRsZXIoKTogdm9pZCB7XG4gICAgICAgIHRoaXMudG9nZ2xlQXNjKCk7XG4gICAgICAgIHRoaXMuYWN0aXZhdGVFeGNsdXNpdmUoKTtcbiAgICAgICAgdGhpcy5zb3J0UHJvamVjdFRpbGVzKCk7XG4gICAgICAgIHRoaXMuX3NhdmVTdGF0ZVRvTG9jYWxTdG9yYWdlKCk7XG4gICAgfVxuICAgIC8vIGFkZHMgY2xhc3MgYGFjdGl2ZWAgdG8gYWN0aXZlIGJ1dHRvbiBhbmQgcmVtb3ZlcyBpdCBmcm9tIGFsbCBvdGhlcnMuXG4gICAgYWN0aXZhdGVFeGNsdXNpdmUoKTogdm9pZCB7XG4gICAgICAgIGNvbnN0IGJ0bnM6IFN5c3RvcmlTb3J0QnV0dG9uW10gPSBBcnJheS5mcm9tKFxuICAgICAgICAgICAgZG9jdW1lbnQucXVlcnlTZWxlY3RvckFsbChcInN5cy1zb3J0LWJ1dHRvblwiKSxcbiAgICAgICAgKTtcbiAgICAgICAgZm9yIChjb25zdCBidG4gb2YgYnRucykge1xuICAgICAgICAgICAgYnRuLmFjdGl2ZSA9IGZhbHNlO1xuICAgICAgICB9XG4gICAgICAgIHRoaXMuYWN0aXZlID0gdHJ1ZTtcbiAgICB9XG5cbiAgICBzb3J0UHJvamVjdFRpbGVzKCk6IHZvaWQge1xuICAgICAgICBjb25zdCBwcm9qZWN0VGlsZXMgPSBBcnJheS5mcm9tKFxuICAgICAgICAgICAgZG9jdW1lbnQucXVlcnlTZWxlY3RvckFsbDxTeXN0b3JpUHJvamVjdFRpbGU+KFwiLnRpbGVcIiksXG4gICAgICAgICk7XG5cbiAgICAgICAgcHJvamVjdFRpbGVzLnNvcnQoKGEsIGIpID0+IHtcbiAgICAgICAgICAgIHN3aXRjaCAodGhpcy50eXBlKSB7XG4gICAgICAgICAgICAgICAgY2FzZSBTb3J0QnV0dG9uVHlwZS5pZDpcbiAgICAgICAgICAgICAgICAgICAgaWYgKHRoaXMuYXNjKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICByZXR1cm4gYi5wayA8IGEucGsgPyAtMSA6IDE7XG4gICAgICAgICAgICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICAgICAgICAgICAgICByZXR1cm4gYS5wayA8IGIucGsgPyAtMSA6IDE7XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICBjYXNlIFNvcnRCdXR0b25UeXBlLm5hbWU6XG4gICAgICAgICAgICAgICAgICAgIC8vIFRvRG86IHN3aXRjaCB4LmRhdGFzZXQubmFtZSEgYmFjayB0byB4Lm5hbWUgaWYgaXQgd29ya3Mgd2l0aCBfbG9hZFN0YXRlRnJvbUxvY2FsU3RvcmFnZVxuICAgICAgICAgICAgICAgICAgICBpZiAodGhpcy5hc2MpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIHJldHVybiBhLmRhdGFzZXQubmFtZSEubG9jYWxlQ29tcGFyZShiLmRhdGFzZXQubmFtZSEpO1xuICAgICAgICAgICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgICAgICAgICAgcmV0dXJuIGIuZGF0YXNldC5uYW1lIS5sb2NhbGVDb21wYXJlKGEuZGF0YXNldC5uYW1lISk7XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICBjYXNlIFNvcnRCdXR0b25UeXBlLnBoYXNlOlxuICAgICAgICAgICAgICAgICAgICBpZiAodGhpcy5hc2MpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIHJldHVybiBQaGFzZU9yZGVyW2IucGhhc2VdIDw9IFBoYXNlT3JkZXJbYS5waGFzZV1cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICA/IC0xXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgOiAxO1xuICAgICAgICAgICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgICAgICAgICAgcmV0dXJuIFBoYXNlT3JkZXJbYS5waGFzZV0gPD0gUGhhc2VPcmRlcltiLnBoYXNlXVxuICAgICAgICAgICAgICAgICAgICAgICAgICAgID8gLTFcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICA6IDE7XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICBkZWZhdWx0OlxuICAgICAgICAgICAgICAgICAgICB0aHJvdyBuZXcgRXJyb3IoXG4gICAgICAgICAgICAgICAgICAgICAgICBgQ2FuJ3QgZmluZCBhIFNvcnRCdXR0b25UeXBlIHR5cGUgZm9yICR7dGhpcy50eXBlfS5gLFxuICAgICAgICAgICAgICAgICAgICApO1xuICAgICAgICAgICAgfVxuICAgICAgICB9KTtcblxuICAgICAgICBpZiAodGlsZUNvbnRhaW5lcikge1xuICAgICAgICAgICAgdGlsZUNvbnRhaW5lci5pbm5lckhUTUwgPSBcIlwiO1xuICAgICAgICAgICAgZm9yIChjb25zdCB0aWxlIG9mIHByb2plY3RUaWxlcykge1xuICAgICAgICAgICAgICAgIHRpbGVDb250YWluZXIuYXBwZW5kQ2hpbGQodGlsZSk7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cblxuICAgICAgICB0aGlzLl9zYXZlU3RhdGVUb0xvY2FsU3RvcmFnZSgpO1xuICAgIH1cblxuICAgIF9zYXZlU3RhdGVUb0xvY2FsU3RvcmFnZSgpOiB2b2lkIHtcbiAgICAgICAgbG9jYWxTdG9yYWdlLnNldEl0ZW0oXG4gICAgICAgICAgICBcInN0YXRlLVN5c3RvcmlTb3J0QnV0dG9uXCIsXG4gICAgICAgICAgICBKU09OLnN0cmluZ2lmeSh7XG4gICAgICAgICAgICAgICAgdHlwZTogdGhpcy50eXBlLFxuICAgICAgICAgICAgICAgIGFzYzogdGhpcy5hc2MsXG4gICAgICAgICAgICB9KSxcbiAgICAgICAgKTtcbiAgICB9XG4gICAgX2xvYWRTdGF0ZUZyb21Mb2NhbFN0b3JhZ2UoKTogdm9pZCB7XG4gICAgICAgIGlmICh0aGlzLmFjdGl2ZSB8fCAhdGhpcy5hY3RpdmUpIHtcbiAgICAgICAgICAgIGNvbnN0IHNvcnRKc29uID0gbG9jYWxTdG9yYWdlLmdldEl0ZW0oXCJzdGF0ZS1TeXN0b3JpU29ydEJ1dHRvblwiKTtcbiAgICAgICAgICAgIGlmIChzb3J0SnNvbikge1xuICAgICAgICAgICAgICAgIGNvbnN0IHN0YXRlOiBTb3J0QnV0dG9uU3RhdGUgPSBKU09OLnBhcnNlKHNvcnRKc29uKTtcbiAgICAgICAgICAgICAgICBpZiAodGhpcy50eXBlID09PSBzdGF0ZS50eXBlKSB7XG4gICAgICAgICAgICAgICAgICAgIHRoaXMuYXNjID0gc3RhdGUuYXNjO1xuICAgICAgICAgICAgICAgICAgICB0aGlzLmFjdGl2ZSA9IHRydWU7XG4gICAgICAgICAgICAgICAgICAgIHRoaXMuc29ydFByb2plY3RUaWxlcygpO1xuICAgICAgICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICAgICAgICAgIGRlbGV0ZSB0aGlzLmRhdGFzZXQuYWN0aXZlO1xuICAgICAgICAgICAgICAgICAgICB0aGlzLmFjdGl2ZSA9IGZhbHNlO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgIH1cbiAgICBjb25uZWN0ZWRDYWxsYmFjaygpOiB2b2lkIHtcbiAgICAgICAgdGhpcy5fbG9hZFN0YXRlRnJvbUxvY2FsU3RvcmFnZSgpO1xuICAgIH1cbn1cblxuY2xhc3MgU3lzdG9yaVBoYXNlQnV0dG9uIGV4dGVuZHMgSFRNTEVsZW1lbnQge1xuICAgIGNvbnN0cnVjdG9yKCkge1xuICAgICAgICBzdXBlcigpO1xuICAgICAgICB0aGlzLmFkZEV2ZW50TGlzdGVuZXIoXCJjbGlja1wiLCAoKSA9PiB0aGlzLmNsaWNrSGFuZGxlcigpKTtcbiAgICB9XG5cbiAgICBnZXQgcGhhc2UoKTogc3RyaW5nIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuZGF0YXNldC5waGFzZSE7XG4gICAgfVxuICAgIHNldCBwaGFzZShwaGFzZTogc3RyaW5nKSB7XG4gICAgICAgIHRoaXMuZGF0YXNldC5waGFzZSA9IHBoYXNlO1xuICAgIH1cblxuICAgIC8vIGhpZGVQaGFzZSA9PT0gaGlkZGVuXG4gICAgZ2V0IGhpZGVQaGFzZSgpOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuY2xhc3NMaXN0LmNvbnRhaW5zKFwiaGlkZS1waGFzZVwiKTtcbiAgICB9XG4gICAgc2V0IGhpZGVQaGFzZShoaWRlOiBib29sZWFuKSB7XG4gICAgICAgIGhpZGVcbiAgICAgICAgICAgID8gdGhpcy5jbGFzc0xpc3QuYWRkKFwiaGlkZS1waGFzZVwiKVxuICAgICAgICAgICAgOiB0aGlzLmNsYXNzTGlzdC5yZW1vdmUoXCJoaWRlLXBoYXNlXCIpO1xuICAgIH1cbiAgICB0b2dnbGVQcm9qZWN0VGlsZXMoc3RhdHVzOiBib29sZWFuKTogdm9pZCB7XG4gICAgICAgIGNvbnN0IHByb2plY3RUaWxlczogU3lzdG9yaVByb2plY3RUaWxlW10gPSBBcnJheS5mcm9tKFxuICAgICAgICAgICAgZG9jdW1lbnQucXVlcnlTZWxlY3RvckFsbChcbiAgICAgICAgICAgICAgICBgc3lzLXByb2plY3QtdGlsZVtkYXRhLXBoYXNlPSR7dGhpcy5waGFzZX1dYCxcbiAgICAgICAgICAgICksXG4gICAgICAgICk7XG4gICAgICAgIGZvciAoY29uc3QgdGlsZSBvZiBwcm9qZWN0VGlsZXMpIHtcbiAgICAgICAgICAgIHRpbGUuaGlkZShzdGF0dXMpO1xuICAgICAgICB9XG4gICAgfVxuICAgIGNsaWNrSGFuZGxlcigpOiB2b2lkIHtcbiAgICAgICAgdGhpcy5oaWRlUGhhc2UgPSAhdGhpcy5oaWRlUGhhc2U7XG4gICAgICAgIHRoaXMuZmlsdGVyUHJvamVjdFRpbGVzKCk7XG4gICAgICAgIHRoaXMuc2hvd1dhcm5pbmdNZXNzYWdlKCk7XG4gICAgICAgIHRoaXMuX3NhdmVTdGF0ZVRvTG9jYWxTdG9yYWdlKCk7XG4gICAgfVxuICAgIGZpbHRlclByb2plY3RUaWxlcygpOiB2b2lkIHtcbiAgICAgICAgdGhpcy5oaWRlUGhhc2VcbiAgICAgICAgICAgID8gdGhpcy50b2dnbGVQcm9qZWN0VGlsZXModHJ1ZSlcbiAgICAgICAgICAgIDogdGhpcy50b2dnbGVQcm9qZWN0VGlsZXMoZmFsc2UpO1xuICAgIH1cbiAgICBzaG93V2FybmluZ01lc3NhZ2UoKTogdm9pZCB7XG4gICAgICAgIGxldCBoaWRkZW5Qcm9qZWN0VGlsZXMgPSBkb2N1bWVudC5xdWVyeVNlbGVjdG9yQWxsPFN5c3RvcmlQcm9qZWN0VGlsZT4oXCIudGlsZS5oaWRkZW5cIik7XG4gICAgICAgIGxldCBzeXNXYXJuaW5nTWVzc2FnZSA9IGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3I8U3lzdG9yaVdhcm5pbmdNZXNzYWdlPihcInN5cy13YXJuaW5nLW1lc3NhZ2VcIik7XG4gICAgICAgIGlmIChzeXNXYXJuaW5nTWVzc2FnZSkgc3lzV2FybmluZ01lc3NhZ2Uud2FybkZpbHRlcmVkUHJvamVjdHMoaGlkZGVuUHJvamVjdFRpbGVzLmxlbmd0aCB8fCAwKTtcbiAgICB9XG4gICAgX3NhdmVTdGF0ZVRvTG9jYWxTdG9yYWdlKCk6IHZvaWQge1xuICAgICAgICBsb2NhbFN0b3JhZ2Uuc2V0SXRlbShcbiAgICAgICAgICAgIGBzdGF0ZS1TeXN0b3JpUGhhc2VCdXR0b24tJHt0aGlzLnBoYXNlfWAsXG4gICAgICAgICAgICBKU09OLnN0cmluZ2lmeSh7XG4gICAgICAgICAgICAgICAgaGlkZVBoYXNlOiB0aGlzLmhpZGVQaGFzZSxcbiAgICAgICAgICAgIH0pLFxuICAgICAgICApO1xuICAgIH1cbiAgICBfbG9hZFN0YXRlRnJvbUxvY2FsU3RvcmFnZSgpOiB2b2lkIHtcbiAgICAgICAgY29uc3Qgc3RhdGVKc29uID0gbG9jYWxTdG9yYWdlLmdldEl0ZW0oXG4gICAgICAgICAgICBgc3RhdGUtU3lzdG9yaVBoYXNlQnV0dG9uLSR7dGhpcy5waGFzZX1gLFxuICAgICAgICApO1xuICAgICAgICBpZiAoc3RhdGVKc29uKSB7XG4gICAgICAgICAgICBjb25zdCBzdGF0ZSA9IEpTT04ucGFyc2Uoc3RhdGVKc29uKTtcbiAgICAgICAgICAgIHRoaXMuaGlkZVBoYXNlID0gc3RhdGUuaGlkZVBoYXNlO1xuICAgICAgICAgICAgdGhpcy5maWx0ZXJQcm9qZWN0VGlsZXMoKTtcbiAgICAgICAgICAgIHRoaXMuc2hvd1dhcm5pbmdNZXNzYWdlKCk7XG4gICAgICAgIH1cbiAgICB9XG4gICAgY29ubmVjdGVkQ2FsbGJhY2soKTogdm9pZCB7XG4gICAgICAgIHRoaXMuX2xvYWRTdGF0ZUZyb21Mb2NhbFN0b3JhZ2UoKTtcbiAgICB9XG59XG5cbmNsYXNzIFN5c3RvcmlTZWFyY2hFbGVtZW50IGV4dGVuZHMgSFRNTEVsZW1lbnQge1xuICAgIC8vIFRoaXMgY3VzdG9tIGVsZW1lbnQgaXMgZm9yIGNvbXBvc2luZyB0aGUgdHdvIGNoaWxkTm9kZXMuXG4gICAgY29uc3RydWN0b3IoKSB7XG4gICAgICAgIHN1cGVyKCk7XG4gICAgfVxufVxuXG5jbGFzcyBTeXN0b3JpU2VhcmNoSW5wdXQgZXh0ZW5kcyBIVE1MSW5wdXRFbGVtZW50IHtcbiAgICB0aW1lb3V0OiBSZXR1cm5UeXBlPHR5cGVvZiBzZXRUaW1lb3V0PiB8IHVuZGVmaW5lZDtcblxuICAgIGNvbnN0cnVjdG9yKCkge1xuICAgICAgICBzdXBlcigpO1xuICAgICAgICB0aGlzLmFkZEV2ZW50TGlzdGVuZXIoXCJrZXl1cFwiLCAoKSA9PiB0aGlzLmNsaWNrSGFuZGxlcigpKTtcbiAgICB9XG5cbiAgICBmaWx0ZXJQcm9qZWN0VGlsZXMoc2VhcmNoUmVzdWx0UGtzOiBudW1iZXJbXSk6IHZvaWQge1xuICAgICAgICBjb25zdCBwcm9qZWN0UGtzID0gdGhpcy5nZXRBbGxMb2NhbFByb2plY3RQa3MoKTtcbiAgICAgICAgLy8gYWxsIHByb2plY3RzIGV4Y2VwdCB0aGUgZm91bmQgcHJvamVjdHNcbiAgICAgICAgY29uc3QgZGlmZmVyZW5jZSA9IHByb2plY3RQa3MuZmlsdGVyKFxuICAgICAgICAgICAgcGsgPT4gIXNlYXJjaFJlc3VsdFBrcy5pbmNsdWRlcyhwayksXG4gICAgICAgICk7XG4gICAgICAgIGZvciAoY29uc3QgcGsgb2YgZGlmZmVyZW5jZSkge1xuICAgICAgICAgICAgY29uc3QgdGlsZSA9IGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3I8U3lzdG9yaVByb2plY3RUaWxlPihcbiAgICAgICAgICAgICAgICBgc3lzLXByb2plY3QtdGlsZVtkYXRhLXBrPVwiJHtwa31cIl1gLFxuICAgICAgICAgICAgKTtcbiAgICAgICAgICAgIGlmICh0aWxlKSB0aWxlLmhpZGUodHJ1ZSk7XG4gICAgICAgIH1cblxuICAgICAgICBjb25zdCBzeXNXYXJuaW5nTWVzc2FnZSA9IGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3I8U3lzdG9yaVdhcm5pbmdNZXNzYWdlPihcInN5cy13YXJuaW5nLW1lc3NhZ2VcIik7XG4gICAgICAgIGlmKHN5c1dhcm5pbmdNZXNzYWdlKSBzeXNXYXJuaW5nTWVzc2FnZS53YXJuRmlsdGVyZWRQcm9qZWN0cyhkaWZmZXJlbmNlLmxlbmd0aCk7XG4gICAgICAgIFxuICAgIH1cblxuICAgIHNob3dBbGxWaXNpYmxlUHJvamVjdHMoKTogdm9pZCB7XG4gICAgICAgIGNvbnN0IHBoYXNlQnRucyA9IG5ldyBNYXAoKTtcbiAgICAgICAgQXJyYXkuZnJvbShcbiAgICAgICAgICAgIGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGw8U3lzdG9yaVBoYXNlQnV0dG9uPihcInN5cy1waGFzZS1idXR0b25cIiksXG4gICAgICAgICkubWFwKHRpbGUgPT4gcGhhc2VCdG5zLnNldCh0aWxlLnBoYXNlLCB0aWxlLmhpZGVQaGFzZSkpO1xuICAgICAgICBjb25zdCBwcm9qZWN0UGtzID0gdGhpcy5nZXRBbGxMb2NhbFByb2plY3RQa3MoKTtcbiAgICAgICAgdmFyIGNvdW50SGlkZGVuUHJvamVjdHMgPSBwcm9qZWN0UGtzLmxlbmd0aDtcbiAgICAgICAgZm9yIChjb25zdCBwayBvZiBwcm9qZWN0UGtzKSB7XG4gICAgICAgICAgICBjb25zdCB0aWxlID0gZG9jdW1lbnQucXVlcnlTZWxlY3RvcjxTeXN0b3JpUHJvamVjdFRpbGU+KFxuICAgICAgICAgICAgICAgIGBzeXMtcHJvamVjdC10aWxlW2RhdGEtcGs9XCIke3BrfVwiXWAsXG4gICAgICAgICAgICApO1xuICAgICAgICAgICAgaWYgKHRpbGUgJiYgIXBoYXNlQnRucy5nZXQodGlsZS5waGFzZSkpIHtcbiAgICAgICAgICAgICAgICB0aWxlLmhpZGUoZmFsc2UpO1xuICAgICAgICAgICAgICAgIGNvdW50SGlkZGVuUHJvamVjdHMtLTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgICAgICBjb25zdCBjYW5jZWxCdXR0b24gPSBkb2N1bWVudC5xdWVyeVNlbGVjdG9yPFN5c3RvcmlTZWFyY2hDYW5jZWxCdXR0b24+KFxuICAgICAgICAgICAgXCJzeXMtc2VhcmNoLWNhbmNlbC1idXR0b25cIixcbiAgICAgICAgKSE7XG4gICAgICAgIGNhbmNlbEJ1dHRvbi52aXNpYmxlID0gZmFsc2U7XG4gICAgICAgIGNvbnN0IHN5c1dhcm5pbmdNZXNzYWdlID0gZG9jdW1lbnQucXVlcnlTZWxlY3RvcjxTeXN0b3JpV2FybmluZ01lc3NhZ2U+KFwic3lzLXdhcm5pbmctbWVzc2FnZVwiKTtcbiAgICAgICAgaWYoc3lzV2FybmluZ01lc3NhZ2UpIHN5c1dhcm5pbmdNZXNzYWdlLndhcm5GaWx0ZXJlZFByb2plY3RzKGNvdW50SGlkZGVuUHJvamVjdHMpO1xuICAgIH1cblxuICAgIGdldEFsbExvY2FsUHJvamVjdFBrcygpOiBudW1iZXJbXSB7XG4gICAgICAgIHJldHVybiBBcnJheS5mcm9tKFxuICAgICAgICAgICAgZG9jdW1lbnQucXVlcnlTZWxlY3RvckFsbDxTeXN0b3JpUHJvamVjdFRpbGU+KGBzeXMtcHJvamVjdC10aWxlYCksXG4gICAgICAgICkubWFwKHRpbGUgPT4ge1xuICAgICAgICAgICAgcmV0dXJuIHRpbGUucGs7XG4gICAgICAgIH0pO1xuICAgIH1cblxuICAgIGFwaVNlYXJjaFByb2plY3RzKCk6IHZvaWQge1xuICAgICAgICBsb2NhbFN0b3JhZ2Uuc2V0SXRlbShcInN5cy1wcm9qZWN0LXNlYXJjaC1pbnB1dFwiLCB0aGlzLnZhbHVlKTtcbiAgICAgICAgZmV0Y2goXCIvYXBpL3Byb2plY3Qvc2VhcmNoL1wiLCB7XG4gICAgICAgICAgICBtZXRob2Q6IFwicHV0XCIsXG4gICAgICAgICAgICBjcmVkZW50aWFsczogXCJzYW1lLW9yaWdpblwiLFxuICAgICAgICAgICAgaGVhZGVyczogaGVhZGVycyxcbiAgICAgICAgICAgIGJvZHk6IEpTT04uc3RyaW5naWZ5KHsgcXVlcnk6IHRoaXMudmFsdWUgfSksXG4gICAgICAgIH0pXG4gICAgICAgICAgICAudGhlbihyZXNwb25zZSA9PiByZXNwb25zZS5qc29uKCkpXG4gICAgICAgICAgICAudGhlbihib2R5ID0+IHtcbiAgICAgICAgICAgICAgICB0aGlzLmZpbHRlclByb2plY3RUaWxlcyhib2R5LnByb2plY3RzKTtcbiAgICAgICAgICAgIH0pO1xuICAgIH1cblxuICAgIHByb2Nlc3NRdWVyeSgpOiB2b2lkIHtcbiAgICAgICAgY29uc3QgY2FuY2VsQnV0dG9uID0gZG9jdW1lbnQucXVlcnlTZWxlY3RvcjxTeXN0b3JpU2VhcmNoQ2FuY2VsQnV0dG9uPihcbiAgICAgICAgICAgIFwic3lzLXNlYXJjaC1jYW5jZWwtYnV0dG9uXCIsXG4gICAgICAgICkhO1xuICAgICAgICBjYW5jZWxCdXR0b24udmlzaWJsZSA9IHRydWU7XG4gICAgICAgIHRoaXMuYXBpU2VhcmNoUHJvamVjdHMoKTtcbiAgICB9XG5cbiAgICBkZWxheWVkQ2xpY2tIYW5kbGVyKCk6IHZvaWQge1xuICAgICAgICB0aGlzLnZhbHVlID09IFwiXCIgPyB0aGlzLnNob3dBbGxWaXNpYmxlUHJvamVjdHMoKSA6IHRoaXMucHJvY2Vzc1F1ZXJ5KCk7XG4gICAgfVxuXG4gICAgY2xpY2tIYW5kbGVyKCk6IHZvaWQge1xuICAgICAgICBpZiAodGhpcy50aW1lb3V0KSBjbGVhclRpbWVvdXQodGhpcy50aW1lb3V0KTtcbiAgICAgICAgdGhpcy50aW1lb3V0ID0gc2V0VGltZW91dCgoKSA9PiB7XG4gICAgICAgICAgICB0aGlzLnZhbHVlID09IFwiXCIgPyB0aGlzLnNob3dBbGxWaXNpYmxlUHJvamVjdHMoKSA6IHRoaXMucHJvY2Vzc1F1ZXJ5KCk7XG4gICAgICAgIH0sIDMwMCk7XG4gICAgfVxufVxuXG5jbGFzcyBTeXN0b3JpU2VhcmNoQ2FuY2VsQnV0dG9uIGV4dGVuZHMgSFRNTEVsZW1lbnQge1xuICAgIGNvbnN0cnVjdG9yKCkge1xuICAgICAgICBzdXBlcigpO1xuICAgICAgICB0aGlzLmFkZEV2ZW50TGlzdGVuZXIoXCJjbGlja1wiLCAoKSA9PiB0aGlzLmNsaWNrSGFuZGxlcigpKTtcbiAgICB9XG4gICAgZ2V0IHZpc2libGUoKTogYm9vbGVhbiB7XG4gICAgICAgIHJldHVybiB0aGlzLmNsYXNzTGlzdC5jb250YWlucyhcInZpc2libGVcIik7XG4gICAgfVxuICAgIHNldCB2aXNpYmxlKHN0YXR1czogYm9vbGVhbikge1xuICAgICAgICB0aGlzLmNsYXNzTGlzdC50b2dnbGUoXCJ2aXNpYmxlXCIsIHN0YXR1cyk7XG4gICAgfVxuICAgIGNsaWNrSGFuZGxlcigpOiB2b2lkIHtcbiAgICAgICAgaWYgKHRoaXMucGFyZW50RWxlbWVudCkge1xuICAgICAgICAgICAgY29uc3QgaW5wdXQgPSB0aGlzLnBhcmVudEVsZW1lbnQucXVlcnlTZWxlY3RvcjxTeXN0b3JpU2VhcmNoSW5wdXQ+KFxuICAgICAgICAgICAgICAgICdpbnB1dFtpcz1cInN5cy1zZWFyY2gtaW5wdXRcIl0nLFxuICAgICAgICAgICAgKTtcbiAgICAgICAgICAgIGlmIChpbnB1dCkge1xuICAgICAgICAgICAgICAgIGlucHV0LnZhbHVlID0gXCJcIjtcbiAgICAgICAgICAgICAgICBpbnB1dC5zaG93QWxsVmlzaWJsZVByb2plY3RzKCk7XG4gICAgICAgICAgICAgICAgdGhpcy52aXNpYmxlID0gZmFsc2U7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICB9XG59XG5cbmNsYXNzIFN5c3RvcmlXYXJuaW5nTWVzc2FnZSBleHRlbmRzIEhUTUxFbGVtZW50IHtcblxuICAgIGNvbnN0cnVjdG9yKCkge1xuICAgICAgICBzdXBlcigpO1xuICAgIH1cblxuICAgIHdhcm5GaWx0ZXJlZFByb2plY3RzKGNvdW50OiBOdW1iZXIpIHtcbiAgICAgICAgbGV0IHJlZ2V4ID0gL1xcJHBoYXNlRmlsdGVyZWRQcm9qZWN0cy9naTtcbiAgICAgICAgaWYgKGNvdW50ID4gMCkge1xuICAgICAgICAgICAgdGhpcy5pbm5lclRleHQgPSAoZG9jdW1lbnQucXVlcnlTZWxlY3RvcihcIiNzeXMtcGhhc2VGaWx0ZXJlZFByb2plY3RzLXRyYW5zbGF0ZWRcIikgYXMgSFRNTEVsZW1lbnQpLmlubmVyVGV4dC5yZXBsYWNlKHJlZ2V4LCBjb3VudC50b1N0cmluZygpKTtcbiAgICAgICAgICAgIHRoaXMuY2xhc3NMaXN0LnJlbW92ZShcImhpZGRlblwiKTtcbiAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgIHRoaXMuY2xhc3NMaXN0LmFkZChcImhpZGRlblwiKTtcbiAgICAgICAgfVxuICAgIH1cblxuICAgIGdldCBoaWRlV2FybmluZ01lc3NhZ2UoKTogYm9vbGVhbiB7XG4gICAgICAgIHJldHVybiB0aGlzLmNsYXNzTGlzdC5jb250YWlucygnaGlkZGVuJyk7XG4gICAgfVxuXG4gICAgc2V0IGhpZGVXYXJuaW5nTWVzc2FnZShoaWRlOiBib29sZWFuKSB7XG4gICAgICAgIGhpZGVcbiAgICAgICAgICAgID8gdGhpcy5jbGFzc0xpc3QuYWRkKCdoaWRkZW4nKVxuICAgICAgICAgICAgOiB0aGlzLmNsYXNzTGlzdC5yZW1vdmUoJ2hpZGRlbicpO1xuICAgIH1cbn1cblxuY3VzdG9tRWxlbWVudHMuZGVmaW5lKFwic3lzLXdhcm5pbmctbWVzc2FnZVwiLCBTeXN0b3JpV2FybmluZ01lc3NhZ2UpO1xuY3VzdG9tRWxlbWVudHMuZGVmaW5lKFwic3lzLXByb2plY3QtdGlsZVwiLCBTeXN0b3JpUHJvamVjdFRpbGUpO1xuY3VzdG9tRWxlbWVudHMuZGVmaW5lKFwic3lzLXNlYXJjaC1pbnB1dFwiLCBTeXN0b3JpU2VhcmNoSW5wdXQsIHtcbiAgICBleHRlbmRzOiBcImlucHV0XCIsXG59KTtcbmN1c3RvbUVsZW1lbnRzLmRlZmluZShcInN5cy1zZWFyY2gtZWxlbWVudFwiLCBTeXN0b3JpU2VhcmNoRWxlbWVudCk7XG5jdXN0b21FbGVtZW50cy5kZWZpbmUoXCJzeXMtc2VhcmNoLWNhbmNlbC1idXR0b25cIiwgU3lzdG9yaVNlYXJjaENhbmNlbEJ1dHRvbik7XG5jdXN0b21FbGVtZW50cy5kZWZpbmUoXCJzeXMtcGhhc2UtYnV0dG9uXCIsIFN5c3RvcmlQaGFzZUJ1dHRvbik7XG5jdXN0b21FbGVtZW50cy5kZWZpbmUoXCJzeXMtc29ydC1idXR0b25cIiwgU3lzdG9yaVNvcnRCdXR0b24pO1xuXG4vLyBsb2FkTG9jYWxTdG9yYWdlKCk7XG5pZiAoZmlsdGVyQmFyKSB7XG4gICAgZmlsdGVyQmFyLmNsYXNzTGlzdC5yZW1vdmUoXCJoaWRkZW5cIik7XG59XG5pZiAodGlsZUNvbnRhaW5lcikge1xuICAgIHRpbGVDb250YWluZXIuY2xhc3NMaXN0LnJlbW92ZShcImhpZGRlblwiKTtcbn1cbiJdLCJzb3VyY2VSb290IjoiIn0=