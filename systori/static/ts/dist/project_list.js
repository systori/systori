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
        this.addEventListener("keyup", () => this.apiSearchProjects());
    }
    apiSearchProjects() {
        const projects = [];
        projects.push(11);
        projects.push(23);
        return projects;
    }
}
// function loadLocalStorage(): void {
//     // const sortJson = localStorage.getItem("state-SystoriSortButton");
//     const phaseJson = localStorage.getItem("state-SystoriPhaseButton");
//     // if (sortJson) {
//     //     const state: SortButtonState = JSON.parse(sortJson);
//     //     const btns: SystoriSortButton[] = Array.from(
//     //         document.querySelectorAll("sys-sort-button"),
//     //     );
//     //     for (const btn of btns) {
//     //         if (btn.type === state.type) {
//     //             btn.asc = state.asc;
//     //             btn.sortProjectTiles(false);
//     //         } else {
//     //             btn.active = false;
//     //         }
//     //     }
//     // }
//     if (phaseJson) {
//         const state: PhaseButtonState[] = JSON.parse(phaseJson);
//         const btns: SystoriPhaseButton[] = Array.from(
//             document.querySelectorAll("sys-phase-button"),
//         );
//         for (const p of state) {
//             if (p.hidePhase) {
//                 for (const btn of btns) {
//                     if (btn.phase === p.phase) {
//                         btn.hidePhase = p.hidePhase;
//                         btn.filterProjectTiles(false);
//                     }
//                 }
//             }
//         }
//     }
// }
customElements.define("sys-search-input", SystoriSearchInput, {
    extends: "input",
});
customElements.define("sys-search-element", SystoriSearchElement);
customElements.define("sys-phase-button", SystoriPhaseButton);
customElements.define("sys-sort-button", SystoriSortButton);
customElements.define("sys-project-tile", SystoriProjectTile);
// loadLocalStorage();
if (filterBar) {
    filterBar.classList.remove("hidden");
}
if (tileContainer) {
    tileContainer.classList.remove("hidden");
}


/***/ })

/******/ });
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8vd2VicGFjay9ib290c3RyYXAiLCJ3ZWJwYWNrOi8vLy4vc3JjL3Byb2plY3RfbGlzdC50cyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiO1FBQUE7UUFDQTs7UUFFQTtRQUNBOztRQUVBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBOztRQUVBO1FBQ0E7O1FBRUE7UUFDQTs7UUFFQTtRQUNBO1FBQ0E7OztRQUdBO1FBQ0E7O1FBRUE7UUFDQTs7UUFFQTtRQUNBO1FBQ0E7UUFDQSwwQ0FBMEMsZ0NBQWdDO1FBQzFFO1FBQ0E7O1FBRUE7UUFDQTtRQUNBO1FBQ0Esd0RBQXdELGtCQUFrQjtRQUMxRTtRQUNBLGlEQUFpRCxjQUFjO1FBQy9EOztRQUVBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQTtRQUNBO1FBQ0E7UUFDQSx5Q0FBeUMsaUNBQWlDO1FBQzFFLGdIQUFnSCxtQkFBbUIsRUFBRTtRQUNySTtRQUNBOztRQUVBO1FBQ0E7UUFDQTtRQUNBLDJCQUEyQiwwQkFBMEIsRUFBRTtRQUN2RCxpQ0FBaUMsZUFBZTtRQUNoRDtRQUNBO1FBQ0E7O1FBRUE7UUFDQSxzREFBc0QsK0RBQStEOztRQUVySDtRQUNBOzs7UUFHQTtRQUNBOzs7Ozs7Ozs7Ozs7OztBQ2xGQSxNQUFNLFNBQVMsR0FBRyxRQUFRLENBQUMsYUFBYSxDQUFDLGFBQWEsQ0FBQyxDQUFDO0FBQ3hELE1BQU0sYUFBYSxHQUFHLFFBQVEsQ0FBQyxhQUFhLENBQUMsaUJBQWlCLENBQUMsQ0FBQztBQUNoRSxJQUFLLFVBUUo7QUFSRCxXQUFLLFVBQVU7SUFDWCx5REFBVztJQUNYLHFEQUFTO0lBQ1QsbURBQVE7SUFDUixxREFBUztJQUNULHVEQUFVO0lBQ1YsbURBQVE7SUFDUixtREFBUTtBQUNaLENBQUMsRUFSSSxVQUFVLEtBQVYsVUFBVSxRQVFkO0FBQ0QsSUFBSyxjQUlKO0FBSkQsV0FBSyxjQUFjO0lBQ2YsMkJB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RDtBQUNuRCx1REFBdUQ7QUFDdkQseURBQXlEO0FBQ3pELHdCQUF3QjtBQUN4QixvQkFBb0I7QUFDcEIsZ0JBQWdCO0FBQ2hCLFlBQVk7QUFDWixRQUFRO0FBQ1IsSUFBSTtBQUVKLGNBQWMsQ0FBQyxNQUFNLENBQUMsa0JBQWtCLEVBQUUsa0JBQWtCLEVBQUU7SUFDMUQsT0FBTyxFQUFFLE9BQU87Q0FDbkIsQ0FBQyxDQUFDO0FBQ0gsY0FBYyxDQUFDLE1BQU0sQ0FBQyxvQkFBb0IsRUFBRSxvQkFBb0IsQ0FBQyxDQUFDO0FBQ2xFLGNBQWMsQ0FBQyxNQUFNLENBQUMsa0JBQWtCLEVBQUUsa0JBQWtCLENBQUMsQ0FBQztBQUM5RCxjQUFjLENBQUMsTUFBTSxDQUFDLGlCQUFpQixFQUFFLGlCQUFpQixDQUFDLENBQUM7QUFDNUQsY0FBYyxDQUFDLE1BQU0sQ0FBQyxrQkFBa0IsRUFBRSxrQkFBa0IsQ0FBQyxDQUFDO0FBRTlELHNCQUFzQjtBQUN0QixJQUFJLFNBQVMsRUFBRTtJQUNYLFNBQVMsQ0FBQyxTQUFTLENBQUMsTUFBTSxDQUFDLFFBQVEsQ0FBQyxDQUFDO0NBQ3hDO0FBQ0QsSUFBSSxhQUFhLEVBQUU7SUFDZixhQUFhLENBQUMsU0FBUyxDQUFDLE1BQU0sQ0FBQyxRQUFRLENBQUMsQ0FBQztDQUM1QyIsImZpbGUiOiJwcm9qZWN0X2xpc3QuanMiLCJzb3VyY2VzQ29udGVudCI6WyIgXHQvLyBUaGUgbW9kdWxlIGNhY2hlXG4gXHR2YXIgaW5zdGFsbGVkTW9kdWxlcyA9IHt9O1xuXG4gXHQvLyBUaGUgcmVxdWlyZSBmdW5jdGlvblxuIFx0ZnVuY3Rpb24gX193ZWJwYWNrX3JlcXVpcmVfXyhtb2R1bGVJZCkge1xuXG4gXHRcdC8vIENoZWNrIGlmIG1vZHVsZSBpcyBpbiBjYWNoZVxuIFx0XHRpZihpbnN0YWxsZWRNb2R1bGVzW21vZHVsZUlkXSkge1xuIFx0XHRcdHJldHVybiBpbnN0YWxsZWRNb2R1bGVzW21vZHVsZUlkXS5leHBvcnRzO1xuIFx0XHR9XG4gXHRcdC8vIENyZWF0ZSBhIG5ldyBtb2R1bGUgKGFuZCBwdXQgaXQgaW50byB0aGUgY2FjaGUpXG4gXHRcdHZhciBtb2R1bGUgPSBpbnN0YWxsZWRNb2R1bGVzW21vZHVsZUlkXSA9IHtcbiBcdFx0XHRpOiBtb2R1bGVJZCxcbiBcdFx0XHRsOiBmYWxzZSxcbiBcdFx0XHRleHBvcnRzOiB7fVxuIFx0XHR9O1xuXG4gXHRcdC8vIEV4ZWN1dGUgdGhlIG1vZHVsZSBmdW5jdGlvblxuIFx0XHRtb2R1bGVzW21vZHVsZUlkXS5jYWxsKG1vZHVsZS5leHBvcnRzLCBtb2R1bGUsIG1vZHVsZS5leHBvcnRzLCBfX3dlYnBhY2tfcmVxdWlyZV9fKTtcblxuIFx0XHQvLyBGbGFnIHRoZSBtb2R1bGUgYXMgbG9hZGVkXG4gXHRcdG1vZHVsZS5sID0gdHJ1ZTtcblxuIFx0XHQvLyBSZXR1cm4gdGhlIGV4cG9ydHMgb2YgdGhlIG1vZHVsZVxuIFx0XHRyZXR1cm4gbW9kdWxlLmV4cG9ydHM7XG4gXHR9XG5cblxuIFx0Ly8gZXhwb3NlIHRoZSBtb2R1bGVzIG9iamVjdCAoX193ZWJwYWNrX21vZHVsZXNfXylcbiBcdF9fd2VicGFja19yZXF1aXJlX18ubSA9IG1vZHVsZXM7XG5cbiBcdC8vIGV4cG9zZSB0aGUgbW9kdWxlIGNhY2hlXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLmMgPSBpbnN0YWxsZWRNb2R1bGVzO1xuXG4gXHQvLyBkZWZpbmUgZ2V0dGVyIGZ1bmN0aW9uIGZvciBoYXJtb255IGV4cG9ydHNcbiBcdF9fd2VicGFja19yZXF1aXJlX18uZCA9IGZ1bmN0aW9uKGV4cG9ydHMsIG5hbWUsIGdldHRlcikge1xuIFx0XHRpZighX193ZWJwYWNrX3JlcXVpcmVfXy5vKGV4cG9ydHMsIG5hbWUpKSB7XG4gXHRcdFx0T2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIG5hbWUsIHsgZW51bWVyYWJsZTogdHJ1ZSwgZ2V0OiBnZXR0ZXIgfSk7XG4gXHRcdH1cbiBcdH07XG5cbiBcdC8vIGRlZmluZSBfX2VzTW9kdWxlIG9uIGV4cG9ydHNcbiBcdF9fd2VicGFja19yZXF1aXJlX18uciA9IGZ1bmN0aW9uKGV4cG9ydHMpIHtcbiBcdFx0aWYodHlwZW9mIFN5bWJvbCAhPT0gJ3VuZGVmaW5lZCcgJiYgU3ltYm9sLnRvU3RyaW5nVGFnKSB7XG4gXHRcdFx0T2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIFN5bWJvbC50b1N0cmluZ1RhZywgeyB2YWx1ZTogJ01vZHVsZScgfSk7XG4gXHRcdH1cbiBcdFx0T2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsICdfX2VzTW9kdWxlJywgeyB2YWx1ZTogdHJ1ZSB9KTtcbiBcdH07XG5cbiBcdC8vIGNyZWF0ZSBhIGZha2UgbmFtZXNwYWNlIG9iamVjdFxuIFx0Ly8gbW9kZSAmIDE6IHZhbHVlIGlzIGEgbW9kdWxlIGlkLCByZXF1aXJlIGl0XG4gXHQvLyBtb2RlICYgMjogbWVyZ2UgYWxsIHByb3BlcnRpZXMgb2YgdmFsdWUgaW50byB0aGUgbnNcbiBcdC8vIG1vZGUgJiA0OiByZXR1cm4gdmFsdWUgd2hlbiBhbHJlYWR5IG5zIG9iamVjdFxuIFx0Ly8gbW9kZSAmIDh8MTogYmVoYXZlIGxpa2UgcmVxdWlyZVxuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy50ID0gZnVuY3Rpb24odmFsdWUsIG1vZGUpIHtcbiBcdFx0aWYobW9kZSAmIDEpIHZhbHVlID0gX193ZWJwYWNrX3JlcXVpcmVfXyh2YWx1ZSk7XG4gXHRcdGlmKG1vZGUgJiA4KSByZXR1cm4gdmFsdWU7XG4gXHRcdGlmKChtb2RlICYgNCkgJiYgdHlwZW9mIHZhbHVlID09PSAnb2JqZWN0JyAmJiB2YWx1ZSAmJiB2YWx1ZS5fX2VzTW9kdWxlKSByZXR1cm4gdmFsdWU7XG4gXHRcdHZhciBucyA9IE9iamVjdC5jcmVhdGUobnVsbCk7XG4gXHRcdF9fd2VicGFja19yZXF1aXJlX18ucihucyk7XG4gXHRcdE9iamVjdC5kZWZpbmVQcm9wZXJ0eShucywgJ2RlZmF1bHQnLCB7IGVudW1lcmFibGU6IHRydWUsIHZhbHVlOiB2YWx1ZSB9KTtcbiBcdFx0aWYobW9kZSAmIDIgJiYgdHlwZW9mIHZhbHVlICE9ICdzdHJpbmcnKSBmb3IodmFyIGtleSBpbiB2YWx1ZSkgX193ZWJwYWNrX3JlcXVpcmVfXy5kKG5zLCBrZXksIGZ1bmN0aW9uKGtleSkgeyByZXR1cm4gdmFsdWVba2V5XTsgfS5iaW5kKG51bGwsIGtleSkpO1xuIFx0XHRyZXR1cm4gbnM7XG4gXHR9O1xuXG4gXHQvLyBnZXREZWZhdWx0RXhwb3J0IGZ1bmN0aW9uIGZvciBjb21wYXRpYmlsaXR5IHdpdGggbm9uLWhhcm1vbnkgbW9kdWxlc1xuIFx0X193ZWJwYWNrX3JlcXVpcmVfXy5uID0gZnVuY3Rpb24obW9kdWxlKSB7XG4gXHRcdHZhciBnZXR0ZXIgPSBtb2R1bGUgJiYgbW9kdWxlLl9fZXNNb2R1bGUgP1xuIFx0XHRcdGZ1bmN0aW9uIGdldERlZmF1bHQoKSB7IHJldHVybiBtb2R1bGVbJ2RlZmF1bHQnXTsgfSA6XG4gXHRcdFx0ZnVuY3Rpb24gZ2V0TW9kdWxlRXhwb3J0cygpIHsgcmV0dXJuIG1vZHVsZTsgfTtcbiBcdFx0X193ZWJwYWNrX3JlcXVpcmVfXy5kKGdldHRlciwgJ2EnLCBnZXR0ZXIpO1xuIFx0XHRyZXR1cm4gZ2V0dGVyO1xuIFx0fTtcblxuIFx0Ly8gT2JqZWN0LnByb3RvdHlwZS5oYXNPd25Qcm9wZXJ0eS5jYWxsXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLm8gPSBmdW5jdGlvbihvYmplY3QsIHByb3BlcnR5KSB7IHJldHVybiBPYmplY3QucHJvdG90eXBlLmhhc093blByb3BlcnR5LmNhbGwob2JqZWN0LCBwcm9wZXJ0eSk7IH07XG5cbiBcdC8vIF9fd2VicGFja19wdWJsaWNfcGF0aF9fXG4gXHRfX3dlYnBhY2tfcmVxdWlyZV9fLnAgPSBcIlwiO1xuXG5cbiBcdC8vIExvYWQgZW50cnkgbW9kdWxlIGFuZCByZXR1cm4gZXhwb3J0c1xuIFx0cmV0dXJuIF9fd2VicGFja19yZXF1aXJlX18oX193ZWJwYWNrX3JlcXVpcmVfXy5zID0gXCIuL3NyYy9wcm9qZWN0X2xpc3QudHNcIik7XG4iLCJjb25zdCBmaWx0ZXJCYXIgPSBkb2N1bWVudC5xdWVyeVNlbGVjdG9yKFwiI2ZpbHRlci1iYXJcIik7XG5jb25zdCB0aWxlQ29udGFpbmVyID0gZG9jdW1lbnQucXVlcnlTZWxlY3RvcihcIiN0aWxlLWNvbnRhaW5lclwiKTtcbmVudW0gUGhhc2VPcmRlciB7XG4gICAgcHJvc3BlY3RpdmUsXG4gICAgdGVuZGVyaW5nLFxuICAgIHBsYW5uaW5nLFxuICAgIGV4ZWN1dGluZyxcbiAgICBzZXR0bGVtZW50LFxuICAgIHdhcnJhbnR5LFxuICAgIGZpbmlzaGVkLFxufVxuZW51bSBTb3J0QnV0dG9uVHlwZSB7XG4gICAgaWQgPSBcImlkXCIsXG4gICAgbmFtZSA9IFwibmFtZVwiLFxuICAgIHBoYXNlID0gXCJwaGFzZVwiLFxufVxuXG5pbnRlcmZhY2UgU29ydEJ1dHRvblN0YXRlIHtcbiAgICB0eXBlOiBTb3J0QnV0dG9uVHlwZTtcbiAgICBhc2M6IGJvb2xlYW47XG59XG5pbnRlcmZhY2UgUGhhc2VCdXR0b25TdGF0ZSB7XG4gICAgaGlkZVBoYXNlOiBib29sZWFuO1xufVxuXG5jbGFzcyBTeXN0b3JpUHJvamVjdFRpbGUgZXh0ZW5kcyBIVE1MRWxlbWVudCB7XG4gICAgY29uc3RydWN0b3IoKSB7XG4gICAgICAgIHN1cGVyKCk7XG4gICAgfVxuICAgIGdldCBwaygpOiBudW1iZXIge1xuICAgICAgICByZXR1cm4gcGFyc2VJbnQodGhpcy5kYXRhc2V0LnBrISk7XG4gICAgfVxuICAgIGdldCBuYW1lKCk6IHN0cmluZyB7XG4gICAgICAgIHJldHVybiB0aGlzLmRhdGFzZXQubmFtZSE7XG4gICAgfVxuICAgIGdldCBwaGFzZSgpOiBQaGFzZU9yZGVyIHtcbiAgICAgICAgcmV0dXJuICh0aGlzLmRhdGFzZXQucGhhc2UgfHwgUGhhc2VPcmRlci5wcm9zcGVjdGl2ZSkgYXMgUGhhc2VPcmRlcjtcbiAgICB9XG4gICAgZ2V0IGhpZGRlbigpOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuY2xhc3NMaXN0LmNvbnRhaW5zKFwiaGlkZGVuXCIpO1xuICAgIH1cbiAgICBoaWRlKGhpZGU6IGJvb2xlYW4pOiB2b2lkIHtcbiAgICAgICAgaGlkZSA/IHRoaXMuY2xhc3NMaXN0LmFkZChcImhpZGRlblwiKSA6IHRoaXMuY2xhc3NMaXN0LnJlbW92ZShcImhpZGRlblwiKTtcbiAgICB9XG59XG5cbmNsYXNzIFN5c3RvcmlTb3J0QnV0dG9uIGV4dGVuZHMgSFRNTEVsZW1lbnQge1xuICAgIGNvbnN0cnVjdG9yKCkge1xuICAgICAgICBzdXBlcigpO1xuICAgICAgICB0aGlzLmFkZEV2ZW50TGlzdGVuZXIoXCJjbGlja1wiLCAoKSA9PiB0aGlzLmNsaWNrSGFuZGxlcigpKTtcbiAgICB9XG4gICAgZ2V0IHR5cGUoKTogU29ydEJ1dHRvblR5cGUge1xuICAgICAgICBzd2l0Y2ggKHRoaXMuZGF0YXNldC50eXBlKSB7XG4gICAgICAgICAgICBjYXNlIFwiaWRcIjpcbiAgICAgICAgICAgICAgICByZXR1cm4gU29ydEJ1dHRvblR5cGUuaWQ7XG4gICAgICAgICAgICBjYXNlIFwibmFtZVwiOlxuICAgICAgICAgICAgICAgIHJldHVybiBTb3J0QnV0dG9uVHlwZS5uYW1lO1xuICAgICAgICAgICAgY2FzZSBcInBoYXNlXCI6XG4gICAgICAgICAgICAgICAgcmV0dXJuIFNvcnRCdXR0b25UeXBlLnBoYXNlO1xuICAgICAgICAgICAgZGVmYXVsdDpcbiAgICAgICAgICAgICAgICB0aHJvdyBFcnJvcihcIkNvdWxkbid0IGNhdGNoIFNvcnRCdXR0b25UeXBlLlwiKTtcbiAgICAgICAgfVxuICAgIH1cbiAgICBzZXQgdHlwZSh0eXBlOiBTb3J0QnV0dG9uVHlwZSkge1xuICAgICAgICB0aGlzLmRhdGFzZXQudHlwZSA9IFNvcnRCdXR0b25UeXBlW3R5cGVdO1xuICAgIH1cblxuICAgIC8vIEFTQy9ERVNDIHNvcnRpbmcgb3JkZXJcbiAgICBnZXQgYXNjKCk6IGJvb2xlYW4ge1xuICAgICAgICByZXR1cm4gdGhpcy5kYXRhc2V0LmFzYyA9PSBcInRydWVcIjtcbiAgICB9XG4gICAgc2V0IGFzYyhhc2M6IGJvb2xlYW4pIHtcbiAgICAgICAgYXNjID8gKHRoaXMuZGF0YXNldC5hc2MgPSBcInRydWVcIikgOiAodGhpcy5kYXRhc2V0LmFzYyA9IFwiZmFsc2VcIik7XG4gICAgfVxuICAgIHRvZ2dsZUFzYygpOiB2b2lkIHtcbiAgICAgICAgdGhpcy5hc2MgPSAhdGhpcy5hc2M7XG4gICAgfVxuXG4gICAgZ2V0IGFjdGl2ZSgpOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuY2xhc3NMaXN0LmNvbnRhaW5zKFwiYWN0aXZlXCIpO1xuICAgIH1cbiAgICBzZXQgYWN0aXZlKHN0YXR1czogYm9vbGVhbikge1xuICAgICAgICB0aGlzLmNsYXNzTGlzdC50b2dnbGUoXCJhY3RpdmVcIiwgc3RhdHVzKTtcbiAgICB9XG5cbiAgICBjbGlja0hhbmRsZXIoKTogdm9pZCB7XG4gICAgICAgIHRoaXMudG9nZ2xlQXNjKCk7XG4gICAgICAgIHRoaXMuYWN0aXZhdGVFeGNsdXNpdmUoKTtcbiAgICAgICAgdGhpcy5zb3J0UHJvamVjdFRpbGVzKCk7XG4gICAgICAgIHRoaXMuX3NhdmVTdGF0ZVRvTG9jYWxTdG9yYWdlKCk7XG4gICAgfVxuICAgIC8vIGFkZHMgY2xhc3MgYGFjdGl2ZWAgdG8gYWN0aXZlIGJ1dHRvbiBhbmQgcmVtb3ZlcyBpdCBmcm9tIGFsbCBvdGhlcnMuXG4gICAgYWN0aXZhdGVFeGNsdXNpdmUoKTogdm9pZCB7XG4gICAgICAgIGNvbnN0IGJ0bnM6IFN5c3RvcmlTb3J0QnV0dG9uW10gPSBBcnJheS5mcm9tKFxuICAgICAgICAgICAgZG9jdW1lbnQucXVlcnlTZWxlY3RvckFsbChcInN5cy1zb3J0LWJ1dHRvblwiKSxcbiAgICAgICAgKTtcbiAgICAgICAgZm9yIChjb25zdCBidG4gb2YgYnRucykge1xuICAgICAgICAgICAgYnRuLmFjdGl2ZSA9IGZhbHNlO1xuICAgICAgICB9XG4gICAgICAgIHRoaXMuYWN0aXZlID0gdHJ1ZTtcbiAgICB9XG5cbiAgICBzb3J0UHJvamVjdFRpbGVzKCk6IHZvaWQge1xuICAgICAgICBjb25zdCBwcm9qZWN0VGlsZXMgPSBBcnJheS5mcm9tKFxuICAgICAgICAgICAgZG9jdW1lbnQucXVlcnlTZWxlY3RvckFsbDxTeXN0b3JpUHJvamVjdFRpbGU+KFwiLnRpbGVcIiksXG4gICAgICAgICk7XG5cbiAgICAgICAgcHJvamVjdFRpbGVzLnNvcnQoKGEsIGIpID0+IHtcbiAgICAgICAgICAgIHN3aXRjaCAodGhpcy50eXBlKSB7XG4gICAgICAgICAgICAgICAgY2FzZSBTb3J0QnV0dG9uVHlwZS5pZDpcbiAgICAgICAgICAgICAgICAgICAgaWYgKHRoaXMuYXNjKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICByZXR1cm4gYi5wayA8IGEucGsgPyAtMSA6IDE7XG4gICAgICAgICAgICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICAgICAgICAgICAgICByZXR1cm4gYS5wayA8IGIucGsgPyAtMSA6IDE7XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICBjYXNlIFNvcnRCdXR0b25UeXBlLm5hbWU6XG4gICAgICAgICAgICAgICAgICAgIC8vIFRvRG86IHN3aXRjaCB4LmRhdGFzZXQubmFtZSEgYmFjayB0byB4Lm5hbWUgaWYgaXQgd29ya3Mgd2l0aCBfbG9hZFN0YXRlRnJvbUxvY2FsU3RvcmFnZVxuICAgICAgICAgICAgICAgICAgICBpZiAodGhpcy5hc2MpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIHJldHVybiBhLmRhdGFzZXQubmFtZSEubG9jYWxlQ29tcGFyZShiLmRhdGFzZXQubmFtZSEpO1xuICAgICAgICAgICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgICAgICAgICAgcmV0dXJuIGIuZGF0YXNldC5uYW1lIS5sb2NhbGVDb21wYXJlKGEuZGF0YXNldC5uYW1lISk7XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICBjYXNlIFNvcnRCdXR0b25UeXBlLnBoYXNlOlxuICAgICAgICAgICAgICAgICAgICBpZiAodGhpcy5hc2MpIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIHJldHVybiBQaGFzZU9yZGVyW2IucGhhc2VdIDw9IFBoYXNlT3JkZXJbYS5waGFzZV1cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICA/IC0xXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgOiAxO1xuICAgICAgICAgICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgICAgICAgICAgcmV0dXJuIFBoYXNlT3JkZXJbYS5waGFzZV0gPD0gUGhhc2VPcmRlcltiLnBoYXNlXVxuICAgICAgICAgICAgICAgICAgICAgICAgICAgID8gLTFcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICA6IDE7XG4gICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICBkZWZhdWx0OlxuICAgICAgICAgICAgICAgICAgICB0aHJvdyBuZXcgRXJyb3IoXG4gICAgICAgICAgICAgICAgICAgICAgICBgQ2FuJ3QgZmluZCBhIFNvcnRCdXR0b25UeXBlIHR5cGUgZm9yICR7dGhpcy50eXBlfS5gLFxuICAgICAgICAgICAgICAgICAgICApO1xuICAgICAgICAgICAgfVxuICAgICAgICB9KTtcblxuICAgICAgICBpZiAodGlsZUNvbnRhaW5lcikge1xuICAgICAgICAgICAgdGlsZUNvbnRhaW5lci5pbm5lckhUTUwgPSBcIlwiO1xuICAgICAgICAgICAgZm9yIChjb25zdCB0aWxlIG9mIHByb2plY3RUaWxlcykge1xuICAgICAgICAgICAgICAgIHRpbGVDb250YWluZXIuYXBwZW5kQ2hpbGQodGlsZSk7XG4gICAgICAgICAgICB9XG4gICAgICAgIH1cblxuICAgICAgICB0aGlzLl9zYXZlU3RhdGVUb0xvY2FsU3RvcmFnZSgpO1xuICAgIH1cblxuICAgIF9zYXZlU3RhdGVUb0xvY2FsU3RvcmFnZSgpOiB2b2lkIHtcbiAgICAgICAgbG9jYWxTdG9yYWdlLnNldEl0ZW0oXG4gICAgICAgICAgICBcInN0YXRlLVN5c3RvcmlTb3J0QnV0dG9uXCIsXG4gICAgICAgICAgICBKU09OLnN0cmluZ2lmeSh7XG4gICAgICAgICAgICAgICAgdHlwZTogdGhpcy50eXBlLFxuICAgICAgICAgICAgICAgIGFzYzogdGhpcy5hc2MsXG4gICAgICAgICAgICB9KSxcbiAgICAgICAgKTtcbiAgICB9XG4gICAgX2xvYWRTdGF0ZUZyb21Mb2NhbFN0b3JhZ2UoKTogdm9pZCB7XG4gICAgICAgIGlmICh0aGlzLmFjdGl2ZSB8fCAhdGhpcy5hY3RpdmUpIHtcbiAgICAgICAgICAgIGNvbnN0IHNvcnRKc29uID0gbG9jYWxTdG9yYWdlLmdldEl0ZW0oXCJzdGF0ZS1TeXN0b3JpU29ydEJ1dHRvblwiKTtcbiAgICAgICAgICAgIGlmIChzb3J0SnNvbikge1xuICAgICAgICAgICAgICAgIGNvbnN0IHN0YXRlOiBTb3J0QnV0dG9uU3RhdGUgPSBKU09OLnBhcnNlKHNvcnRKc29uKTtcbiAgICAgICAgICAgICAgICBpZiAodGhpcy50eXBlID09PSBzdGF0ZS50eXBlKSB7XG4gICAgICAgICAgICAgICAgICAgIHRoaXMuYXNjID0gc3RhdGUuYXNjO1xuICAgICAgICAgICAgICAgICAgICB0aGlzLmFjdGl2ZSA9IHRydWU7XG4gICAgICAgICAgICAgICAgICAgIHRoaXMuc29ydFByb2plY3RUaWxlcygpO1xuICAgICAgICAgICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgICAgICAgICAgIGRlbGV0ZSB0aGlzLmRhdGFzZXQuYWN0aXZlO1xuICAgICAgICAgICAgICAgICAgICB0aGlzLmFjdGl2ZSA9IGZhbHNlO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgIH1cbiAgICBjb25uZWN0ZWRDYWxsYmFjaygpOiB2b2lkIHtcbiAgICAgICAgdGhpcy5fbG9hZFN0YXRlRnJvbUxvY2FsU3RvcmFnZSgpO1xuICAgIH1cbn1cblxuY2xhc3MgU3lzdG9yaVBoYXNlQnV0dG9uIGV4dGVuZHMgSFRNTEVsZW1lbnQge1xuICAgIGNvbnN0cnVjdG9yKCkge1xuICAgICAgICBzdXBlcigpO1xuICAgICAgICB0aGlzLmFkZEV2ZW50TGlzdGVuZXIoXCJjbGlja1wiLCAoKSA9PiB0aGlzLmNsaWNrSGFuZGxlcigpKTtcbiAgICB9XG5cbiAgICBnZXQgcGhhc2UoKTogc3RyaW5nIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuZGF0YXNldC5waGFzZSE7XG4gICAgfVxuICAgIHNldCBwaGFzZShwaGFzZTogc3RyaW5nKSB7XG4gICAgICAgIHRoaXMuZGF0YXNldC5waGFzZSA9IHBoYXNlO1xuICAgIH1cblxuICAgIC8vIGhpZGVQaGFzZSA9PT0gaGlkZGVuXG4gICAgZ2V0IGhpZGVQaGFzZSgpOiBib29sZWFuIHtcbiAgICAgICAgcmV0dXJuIHRoaXMuY2xhc3NMaXN0LmNvbnRhaW5zKFwiaGlkZS1waGFzZVwiKTtcbiAgICB9XG4gICAgc2V0IGhpZGVQaGFzZShoaWRlOiBib29sZWFuKSB7XG4gICAgICAgIGhpZGVcbiAgICAgICAgICAgID8gdGhpcy5jbGFzc0xpc3QuYWRkKFwiaGlkZS1waGFzZVwiKVxuICAgICAgICAgICAgOiB0aGlzLmNsYXNzTGlzdC5yZW1vdmUoXCJoaWRlLXBoYXNlXCIpO1xuICAgIH1cbiAgICB0b2dnbGVQcm9qZWN0VGlsZXMoc3RhdHVzOiBib29sZWFuKTogdm9pZCB7XG4gICAgICAgIGNvbnN0IHByb2plY3RUaWxlczogU3lzdG9yaVByb2plY3RUaWxlW10gPSBBcnJheS5mcm9tKFxuICAgICAgICAgICAgZG9jdW1lbnQucXVlcnlTZWxlY3RvckFsbChcbiAgICAgICAgICAgICAgICBgc3lzLXByb2plY3QtdGlsZVtkYXRhLXBoYXNlPSR7dGhpcy5waGFzZX1dYCxcbiAgICAgICAgICAgICksXG4gICAgICAgICk7XG4gICAgICAgIGZvciAoY29uc3QgdGlsZSBvZiBwcm9qZWN0VGlsZXMpIHtcbiAgICAgICAgICAgIHRpbGUuaGlkZShzdGF0dXMpO1xuICAgICAgICB9XG4gICAgfVxuICAgIGNsaWNrSGFuZGxlcigpOiB2b2lkIHtcbiAgICAgICAgdGhpcy5oaWRlUGhhc2UgPSAhdGhpcy5oaWRlUGhhc2U7XG4gICAgICAgIHRoaXMuZmlsdGVyUHJvamVjdFRpbGVzKCk7XG4gICAgICAgIHRoaXMuX3NhdmVTdGF0ZVRvTG9jYWxTdG9yYWdlKCk7XG4gICAgfVxuICAgIGZpbHRlclByb2plY3RUaWxlcygpOiB2b2lkIHtcbiAgICAgICAgdGhpcy5oaWRlUGhhc2VcbiAgICAgICAgICAgID8gdGhpcy50b2dnbGVQcm9qZWN0VGlsZXModHJ1ZSlcbiAgICAgICAgICAgIDogdGhpcy50b2dnbGVQcm9qZWN0VGlsZXMoZmFsc2UpO1xuICAgIH1cbiAgICBfc2F2ZVN0YXRlVG9Mb2NhbFN0b3JhZ2UoKTogdm9pZCB7XG4gICAgICAgIGxvY2FsU3RvcmFnZS5zZXRJdGVtKFxuICAgICAgICAgICAgYHN0YXRlLVN5c3RvcmlQaGFzZUJ1dHRvbi0ke3RoaXMucGhhc2V9YCxcbiAgICAgICAgICAgIEpTT04uc3RyaW5naWZ5KHtcbiAgICAgICAgICAgICAgICBoaWRlUGhhc2U6IHRoaXMuaGlkZVBoYXNlLFxuICAgICAgICAgICAgfSksXG4gICAgICAgICk7XG4gICAgfVxuICAgIF9sb2FkU3RhdGVGcm9tTG9jYWxTdG9yYWdlKCk6IHZvaWQge1xuICAgICAgICBjb25zdCBzdGF0ZUpzb24gPSBsb2NhbFN0b3JhZ2UuZ2V0SXRlbShcbiAgICAgICAgICAgIGBzdGF0ZS1TeXN0b3JpUGhhc2VCdXR0b24tJHt0aGlzLnBoYXNlfWAsXG4gICAgICAgICk7XG4gICAgICAgIGlmIChzdGF0ZUpzb24pIHtcbiAgICAgICAgICAgIGNvbnN0IHN0YXRlID0gSlNPTi5wYXJzZShzdGF0ZUpzb24pO1xuICAgICAgICAgICAgdGhpcy5oaWRlUGhhc2UgPSBzdGF0ZS5oaWRlUGhhc2U7XG4gICAgICAgICAgICB0aGlzLmZpbHRlclByb2plY3RUaWxlcygpO1xuICAgICAgICB9XG4gICAgfVxuICAgIGNvbm5lY3RlZENhbGxiYWNrKCk6IHZvaWQge1xuICAgICAgICB0aGlzLl9sb2FkU3RhdGVGcm9tTG9jYWxTdG9yYWdlKCk7XG4gICAgfVxufVxuXG5jbGFzcyBTeXN0b3JpU2VhcmNoRWxlbWVudCBleHRlbmRzIEhUTUxFbGVtZW50IHtcbiAgICAvLyBUaGlzIGN1c3RvbSBlbGVtZW50IGlzIGZvciBjb21wb3NpbmcgdGhlIHR3byBjaGlsZE5vZGVzLlxuICAgIGNvbnN0cnVjdG9yKCkge1xuICAgICAgICBzdXBlcigpO1xuICAgIH1cbn1cblxuY2xhc3MgU3lzdG9yaVNlYXJjaElucHV0IGV4dGVuZHMgSFRNTElucHV0RWxlbWVudCB7XG4gICAgY29uc3RydWN0b3IoKSB7XG4gICAgICAgIHN1cGVyKCk7XG4gICAgICAgIHRoaXMuYWRkRXZlbnRMaXN0ZW5lcihcImtleXVwXCIsICgpID0+IHRoaXMuYXBpU2VhcmNoUHJvamVjdHMoKSk7XG4gICAgfVxuXG4gICAgYXBpU2VhcmNoUHJvamVjdHMoKTogbnVtYmVyW10ge1xuICAgICAgICBjb25zdCBwcm9qZWN0cyA9IFtdIGFzIG51bWJlcltdO1xuICAgICAgICBwcm9qZWN0cy5wdXNoKDExKTtcbiAgICAgICAgcHJvamVjdHMucHVzaCgyMyk7XG4gICAgICAgIHJldHVybiBwcm9qZWN0cztcbiAgICB9XG59XG5cbi8vIGZ1bmN0aW9uIGxvYWRMb2NhbFN0b3JhZ2UoKTogdm9pZCB7XG4vLyAgICAgLy8gY29uc3Qgc29ydEpzb24gPSBsb2NhbFN0b3JhZ2UuZ2V0SXRlbShcInN0YXRlLVN5c3RvcmlTb3J0QnV0dG9uXCIpO1xuLy8gICAgIGNvbnN0IHBoYXNlSnNvbiA9IGxvY2FsU3RvcmFnZS5nZXRJdGVtKFwic3RhdGUtU3lzdG9yaVBoYXNlQnV0dG9uXCIpO1xuLy8gICAgIC8vIGlmIChzb3J0SnNvbikge1xuLy8gICAgIC8vICAgICBjb25zdCBzdGF0ZTogU29ydEJ1dHRvblN0YXRlID0gSlNPTi5wYXJzZShzb3J0SnNvbik7XG4vLyAgICAgLy8gICAgIGNvbnN0IGJ0bnM6IFN5c3RvcmlTb3J0QnV0dG9uW10gPSBBcnJheS5mcm9tKFxuLy8gICAgIC8vICAgICAgICAgZG9jdW1lbnQucXVlcnlTZWxlY3RvckFsbChcInN5cy1zb3J0LWJ1dHRvblwiKSxcbi8vICAgICAvLyAgICAgKTtcbi8vICAgICAvLyAgICAgZm9yIChjb25zdCBidG4gb2YgYnRucykge1xuLy8gICAgIC8vICAgICAgICAgaWYgKGJ0bi50eXBlID09PSBzdGF0ZS50eXBlKSB7XG4vLyAgICAgLy8gICAgICAgICAgICAgYnRuLmFzYyA9IHN0YXRlLmFzYztcbi8vICAgICAvLyAgICAgICAgICAgICBidG4uc29ydFByb2plY3RUaWxlcyhmYWxzZSk7XG4vLyAgICAgLy8gICAgICAgICB9IGVsc2Uge1xuLy8gICAgIC8vICAgICAgICAgICAgIGJ0bi5hY3RpdmUgPSBmYWxzZTtcbi8vICAgICAvLyAgICAgICAgIH1cbi8vICAgICAvLyAgICAgfVxuLy8gICAgIC8vIH1cbi8vICAgICBpZiAocGhhc2VKc29uKSB7XG4vLyAgICAgICAgIGNvbnN0IHN0YXRlOiBQaGFzZUJ1dHRvblN0YXRlW10gPSBKU09OLnBhcnNlKHBoYXNlSnNvbik7XG4vLyAgICAgICAgIGNvbnN0IGJ0bnM6IFN5c3RvcmlQaGFzZUJ1dHRvbltdID0gQXJyYXkuZnJvbShcbi8vICAgICAgICAgICAgIGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3JBbGwoXCJzeXMtcGhhc2UtYnV0dG9uXCIpLFxuLy8gICAgICAgICApO1xuLy8gICAgICAgICBmb3IgKGNvbnN0IHAgb2Ygc3RhdGUpIHtcbi8vICAgICAgICAgICAgIGlmIChwLmhpZGVQaGFzZSkge1xuLy8gICAgICAgICAgICAgICAgIGZvciAoY29uc3QgYnRuIG9mIGJ0bnMpIHtcbi8vICAgICAgICAgICAgICAgICAgICAgaWYgKGJ0bi5waGFzZSA9PT0gcC5waGFzZSkge1xuLy8gICAgICAgICAgICAgICAgICAgICAgICAgYnRuLmhpZGVQaGFzZSA9IHAuaGlkZVBoYXNlO1xuLy8gICAgICAgICAgICAgICAgICAgICAgICAgYnRuLmZpbHRlclByb2plY3RUaWxlcyhmYWxzZSk7XG4vLyAgICAgICAgICAgICAgICAgICAgIH1cbi8vICAgICAgICAgICAgICAgICB9XG4vLyAgICAgICAgICAgICB9XG4vLyAgICAgICAgIH1cbi8vICAgICB9XG4vLyB9XG5cbmN1c3RvbUVsZW1lbnRzLmRlZmluZShcInN5cy1zZWFyY2gtaW5wdXRcIiwgU3lzdG9yaVNlYXJjaElucHV0LCB7XG4gICAgZXh0ZW5kczogXCJpbnB1dFwiLFxufSk7XG5jdXN0b21FbGVtZW50cy5kZWZpbmUoXCJzeXMtc2VhcmNoLWVsZW1lbnRcIiwgU3lzdG9yaVNlYXJjaEVsZW1lbnQpO1xuY3VzdG9tRWxlbWVudHMuZGVmaW5lKFwic3lzLXBoYXNlLWJ1dHRvblwiLCBTeXN0b3JpUGhhc2VCdXR0b24pO1xuY3VzdG9tRWxlbWVudHMuZGVmaW5lKFwic3lzLXNvcnQtYnV0dG9uXCIsIFN5c3RvcmlTb3J0QnV0dG9uKTtcbmN1c3RvbUVsZW1lbnRzLmRlZmluZShcInN5cy1wcm9qZWN0LXRpbGVcIiwgU3lzdG9yaVByb2plY3RUaWxlKTtcblxuLy8gbG9hZExvY2FsU3RvcmFnZSgpO1xuaWYgKGZpbHRlckJhcikge1xuICAgIGZpbHRlckJhci5jbGFzc0xpc3QucmVtb3ZlKFwiaGlkZGVuXCIpO1xufVxuaWYgKHRpbGVDb250YWluZXIpIHtcbiAgICB0aWxlQ29udGFpbmVyLmNsYXNzTGlzdC5yZW1vdmUoXCJoaWRkZW5cIik7XG59XG4iXSwic291cmNlUm9vdCI6IiJ9